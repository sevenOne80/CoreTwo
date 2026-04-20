import os
import uuid
from datetime import datetime
from flask import render_template, redirect, url_for, flash, session, request, current_app, abort
from flask_login import login_required, current_user
from app.portal import portal
from app.portal.forms import (
    IdentityForm, UploadExtractForm, InvestorProfileForm,
    ProductSelectionForm, SignatureForm
)
from app.extensions import db
from app.models import User, PensionExtract, EligibilityResult, InvestorProfile, Product, Subscription
from app.utils.pdf_parser import parse_pension_extract
from app.utils.eligibility import compute_eligibility
from app.utils.profile import compute_investor_profile


ONBOARDING_STEPS = 6


@portal.route('/dashboard')
@login_required
def dashboard():
    return render_template('portal/dashboard.html', user=current_user)


@portal.route('/onboarding/<int:step>', methods=['GET', 'POST'])
@login_required
def onboarding_step(step):
    if step < 1 or step > ONBOARDING_STEPS:
        abort(404)

    if step == 1:
        form = IdentityForm()
        if form.validate_on_submit():
            current_user.national_number = form.national_number.data
            current_user.birth_date = form.birth_date.data
            current_user.phone = form.phone.data
            current_user.onboarding_step = max(current_user.onboarding_step, 1)
            db.session.commit()
            return redirect(url_for('portal.onboarding_step', step=2))
        return render_template('portal/onboarding/step1_identity.html',
                               form=form, step=step, total=ONBOARDING_STEPS)

    if step == 2:
        if current_user.onboarding_step < 1:
            return redirect(url_for('portal.onboarding_step', step=1))
        form = UploadExtractForm()
        if form.validate_on_submit():
            file = form.extract_file.data
            filename = f"{uuid.uuid4().hex}.pdf"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            extract = PensionExtract(
                user_id=current_user.id,
                filename=file.filename,
                file_path=file_path,
            )
            db.session.add(extract)
            db.session.flush()

            parsed = parse_pension_extract(file_path)
            extract.parsed_data = parsed

            current_user.onboarding_step = max(current_user.onboarding_step, 2)
            db.session.commit()
            return redirect(url_for('portal.onboarding_step', step=3))
        return render_template('portal/onboarding/step2_upload.html',
                               form=form, step=step, total=ONBOARDING_STEPS)

    if step == 3:
        if current_user.onboarding_step < 2:
            return redirect(url_for('portal.onboarding_step', step=2))
        extract = current_user.latest_extract
        if not extract:
            return redirect(url_for('portal.onboarding_step', step=2))

        if not extract.eligibility:
            result = compute_eligibility(extract.parsed_data)
            eligibility = EligibilityResult(
                extract_id=extract.id,
                user_id=current_user.id,
                is_eligible=result['eligible'],
                transferable_amount=result.get('amount'),
                current_institution=result.get('institution'),
                branch21_contracts=str(result.get('contracts', [])),
                reason=result.get('reason'),
            )
            db.session.add(eligibility)
            current_user.onboarding_step = max(current_user.onboarding_step, 3)
            db.session.commit()

        return render_template('portal/onboarding/step3_analysis.html',
                               extract=extract, eligibility=extract.eligibility,
                               step=step, total=ONBOARDING_STEPS)

    if step == 4:
        if current_user.onboarding_step < 3:
            return redirect(url_for('portal.onboarding_step', step=3))
        eligibility = current_user.latest_eligibility
        if not eligibility or not eligibility.is_eligible:
            return redirect(url_for('portal.onboarding_step', step=3))

        form = InvestorProfileForm()
        if form.validate_on_submit():
            answers = {
                'q1': form.q1.data, 'q2': form.q2.data, 'q3': form.q3.data,
                'q4': form.q4.data, 'q5': form.q5.data, 'q6': form.q6.data,
                'q7': form.q7.data, 'q8': form.q8.data,
            }
            profile_result = compute_investor_profile(answers)

            profile = current_user.profile or InvestorProfile(user_id=current_user.id)
            profile.risk_score = profile_result['score']
            profile.profile_type = profile_result['type']
            profile.questionnaire_answers = answers
            if not current_user.profile:
                db.session.add(profile)

            current_user.onboarding_step = max(current_user.onboarding_step, 4)
            db.session.commit()
            return redirect(url_for('portal.onboarding_step', step=5))

        return render_template('portal/onboarding/step4_profile.html',
                               form=form, step=step, total=ONBOARDING_STEPS)

    if step == 5:
        if current_user.onboarding_step < 4:
            return redirect(url_for('portal.onboarding_step', step=4))
        profile = current_user.profile
        if not profile:
            return redirect(url_for('portal.onboarding_step', step=4))

        products = Product.query.filter_by(
            is_active=True, risk_level=profile.profile_type
        ).all()

        form = ProductSelectionForm()
        form.product_id.choices = [(p.id, p.name(session.get('lang', 'fr'))) for p in products]

        if form.validate_on_submit():
            eligibility = current_user.latest_eligibility
            subscription = Subscription(
                user_id=current_user.id,
                product_id=form.product_id.data,
                amount=form.amount.data,
                reference=f"CT-{uuid.uuid4().hex[:8].upper()}",
            )
            db.session.add(subscription)
            current_user.onboarding_step = max(current_user.onboarding_step, 5)
            db.session.commit()
            return redirect(url_for('portal.onboarding_step', step=6))

        eligibility = current_user.latest_eligibility
        return render_template('portal/onboarding/step5_product.html',
                               form=form, products=products, profile=profile,
                               eligibility=eligibility, step=step, total=ONBOARDING_STEPS)

    if step == 6:
        if current_user.onboarding_step < 5:
            return redirect(url_for('portal.onboarding_step', step=5))
        subscription = current_user.subscriptions.filter_by(status='draft').order_by(
            Subscription.created_at.desc()
        ).first()
        if not subscription:
            return redirect(url_for('portal.onboarding_step', step=5))

        form = SignatureForm()
        if form.validate_on_submit():
            subscription.status = 'pending_signature'
            subscription.signed_at = datetime.utcnow()
            current_user.onboarding_step = 6
            db.session.commit()
            return redirect(url_for('portal.onboarding_complete'))

        return render_template('portal/onboarding/step6_sign.html',
                               form=form, subscription=subscription,
                               step=step, total=ONBOARDING_STEPS)


@portal.route('/onboarding/complete')
@login_required
def onboarding_complete():
    return render_template('portal/onboarding/complete.html')


@portal.route('/documents')
@login_required
def documents():
    extracts = current_user.extracts.order_by(PensionExtract.uploaded_at.desc()).all()
    return render_template('portal/documents.html', extracts=extracts)


@portal.route('/profile')
@login_required
def profile():
    return render_template('portal/profile.html', user=current_user)
