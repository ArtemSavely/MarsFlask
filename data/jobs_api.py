from flask import Blueprint, make_response, jsonify, request
from . import db_session
from .jobs import Jobs

blueprint = Blueprint('jobs_api', __name__)

@blueprint.route('/api/jobs', methods=['GET'])
def get_all_news():
    db_sess = db_session.create_session()
    jobs = [n.to_dict(only=("id", "team_leader", "job", "work_size",
                            "collaborators", "start_date", "end_date", "is_finished")) for n in db_sess.query(Jobs).all()]
    return jsonify({"jobs": jobs})


@blueprint.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_one_news(job_id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter(Jobs.id == job_id).first()
    if not jobs:
        return make_response(jsonify({"Error": "not found"}), 404)
    return jsonify({"news": jobs.to_dict(only=("id", "team_leader", "job", "work_size",
                            "collaborators", "start_date", "end_date", "is_finished"))})


@blueprint.route('/api/jobs', methods=['POST'])
def create_news():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['team_leader', 'job', 'work_size', 'collaborators',
                  'start_date', 'end_date', 'is_finished']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    job = Jobs(
        team_leader=request.json['team_leader'],
        job=request.json['job'],
        work_size=request.json['work_size'],
        collaborators=request.json['collaborators'],
        start_date=request.json['start_date'],
        end_date=request.json['end_date'],
        is_finished=request.json['is_finished']
    )
    db_sess.add(job)
    db_sess.commit()
    return jsonify({'id': job.id})
