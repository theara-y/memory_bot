from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask_login import current_user
from sqlalchemy import or_
from sqlalchemy.sql import func

from .. import db
from ..models import Memory
from .forms import CreateMemoryForm, EditMemoryForm, SubmitTestForm

from datetime import datetime, timedelta

bp = Blueprint('app', __name__)


@bp.before_request
def check_login():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))


@bp.route('/')
def index():
    return redirect(url_for('app.dashboard'))


@bp.route('/dashboard')
def dashboard():
    current_timestamp = datetime.utcnow()

    stats = db.session.query(
        db.func.count().filter(Memory.user_id==current_user.id).label('total_memories'),
        db.func.count().filter(Memory.user_id==current_user.id, Memory.training_status=='active').label('active'),
        db.func.count().filter(Memory.user_id==current_user.id, Memory.training_status=='inactive').label('inactive'),
        db.func.count().filter(Memory.user_id==current_user.id, Memory.training_status=='completed').label('completed'),
        db.func.sum(Memory.total_recall_count).filter(Memory.user_id==current_user.id).label('total_recall_attempts'),
        db.func.count().filter(Memory.user_id==current_user.id, Memory.training_status=='active', Memory.last_recall_outcome=='perfect').label('perfect'),
        db.func.count().filter(Memory.user_id==current_user.id, Memory.training_status=='active', Memory.last_recall_outcome=='partial').label('partial'),
        db.func.count().filter(Memory.user_id==current_user.id, Memory.training_status=='active', Memory.last_recall_outcome=='failed').label('failed'),
        db.func.max(Memory.last_recall_at).filter(Memory.user_id==current_user.id, Memory.training_status=='active').label('last_recall_at'),
        db.func.min(Memory.next_recall_at).filter(Memory.user_id==current_user.id, Memory.training_status=='active').label('next_recall_at'),
        db.func.count().filter(Memory.user_id==current_user.id, Memory.training_status=='active', Memory.next_recall_at<=current_timestamp).label('memories_to_test'),
    ).one()

    return render_template('app/dashboard.html', stats=stats)


@bp.route('/create_memory', methods=['GET', 'POST'])
def create_memory():
    form = CreateMemoryForm()

    if form.validate_on_submit():
        memory = Memory(
            prompt=form.prompt.data,
            answer=form.answer.data,
            user_id=current_user.id
        )
        db.session.add(memory)
        db.session.commit()

        flash('Memory created', category='success')

        return redirect(url_for('app.dashboard'))
        
    return render_template('app/create_memory.html', form=form)


@bp.route('/view_memories', methods=['GET'])
def view_memories():
    memories = Memory.query.filter_by(user_id=current_user.id).all()
    return render_template('app/view_memories.html', memories=memories)


@bp.route('/view_memory/<int:id>', methods=['GET'])
def view_memory(id):
    memory = Memory.query.filter_by(id=id, user_id=current_user.id).first()
    return render_template('app/view_memory.html', memory=memory)


@bp.route('/edit_memory/<int:id>', methods=['GET', 'POST'])
def edit_memory(id):
    memory = Memory.query.filter_by(id=id, user_id=current_user.id).first()
    form = EditMemoryForm(
        prompt=memory.prompt,
        answer=memory.answer
    )

    if form.validate_on_submit():
        memory.prompt = form.prompt.data
        memory.answer = form.answer.data
        db.session.commit()
        flash('Memory updated', category='success')
        return redirect(url_for('app.view_memory', id=id))

    return render_template('app/edit_memory.html', form=form)


@bp.route('/delete_memory/<int:id>', methods=['GET'])
def delete_memory(id):
    memory = Memory.query.filter_by(id=id, user_id=current_user.id).first()

    if memory:
        db.session.delete(memory)
        db.session.commit()
        flash('Memory deleted', category='success')

    return redirect(url_for('app.view_memories'))


@bp.route('/test_memory/<int:id>', methods=['GET', 'POST'])
def test_memory(id):
    memory = Memory.query.filter_by(id=id, user_id=current_user.id).first()

    form = SubmitTestForm()
    if form.validate_on_submit():
        memory.last_recall_outcome = form.result.data
        memory.last_recall_at = datetime.utcnow()
        memory.last_modified_at = datetime.utcnow()
        memory.total_recall_count += 1

        if form.result.data == 'perfect':
            memory.perfect_recall_count += 1
            if memory.recall_duration_days == 0:
                memory.recall_duration_days = 1
            else:
                memory.recall_duration_days *= 2

        elif form.result.data == 'partial':
            memory.partial_recall_count += 1
            memory.recall_duration_days = 1

        else:
            memory.failed_recall_count += 1
            memory.recall_duration_days = 1

        memory.next_recall_at = datetime.utcnow() + timedelta(days=memory.recall_duration_days)

        db.session.commit()

        flash('Result submitted', category='success')

        return redirect(url_for('app.next_memory_test'))

    return render_template('app/test_memory.html', memory=memory, form=form)


@bp.route('/next_memory_test', methods=['GET'])
def next_memory_test():
    current_time = datetime.utcnow()

    memory = Memory.query.filter(
        Memory.user_id==current_user.id,
        Memory.training_status=='active',
        or_(
            Memory.next_recall_at.is_(None),
            Memory.next_recall_at <= current_time
        )
    ).order_by(func.random()).first()

    if not memory:
        flash('Training completed for today. Good job!', category='success')
        return redirect(url_for('app.dashboard'))

    return redirect(url_for('app.test_memory', id=memory.id))