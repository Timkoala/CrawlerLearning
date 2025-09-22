from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from models.job import CrawlJob, CrawlResult
from crawler.process_manager import ProcessManager
from config.config_manager import ConfigManager
from config.sites_config import load_sites_config, get_sites_by_country, get_sites_by_category
from web.auth import require_api_key, validate_json
import json

bp = Blueprint('web', __name__)

# Initialize managers
process_manager = ProcessManager()
config_manager = ConfigManager()

@bp.route('/')
def index():
    # Get system stats
    stats = process_manager.get_system_stats()
    return render_template('index.html', stats=stats)

@bp.route('/jobs')
def jobs():
    # Get all jobs from database
    jobs = CrawlJob.query.all()
    return render_template('jobs.html', jobs=jobs)

@bp.route('/api/jobs', methods=['GET'])
@require_api_key
def api_get_jobs():
    jobs = CrawlJob.query.all()
    return jsonify([job.to_dict() for job in jobs])

@bp.route('/api/jobs', methods=['POST'])
@require_api_key
@validate_json
def api_create_job():
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name') or not data.get('target_url'):
        return jsonify({'success': False, 'error': 'Name and target_url are required'}), 400
    
    # Prepare custom rules
    custom_rules = None
    if data.get('custom_rules'):
        import json
        custom_rules = json.dumps(data['custom_rules'])
    
    # Create job in database
    job = CrawlJob(
        name=data['name'],
        target_url=data['target_url'],
        max_depth=data.get('max_depth', 1),
        custom_rules=custom_rules,
        status='saved'
    )
    
    from app import db as app_db
    app_db.session.add(job)
    app_db.session.commit()
    
    return jsonify({'success': True, 'job': job.to_dict()})

@bp.route('/api/jobs/<int:job_id>/start', methods=['POST'])
@require_api_key
def api_start_job(job_id):
    job = CrawlJob.query.get_or_404(job_id)
    
    # Start the crawl job
    try:
        process_manager.start_job(job.id, job.target_url, job.max_depth, job.custom_rules)
        job.status = 'running'
        from app import db as app_db
        app_db.session.commit()
        return jsonify({'success': True, 'job': job.to_dict()})
    except Exception as e:
        job.status = 'failed'
        from app import db as app_db
        app_db.session.commit()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/jobs/<int:job_id>/stop', methods=['POST'])
@require_api_key
def api_stop_job(job_id):
    job = CrawlJob.query.get_or_404(job_id)
    
    if job.status == 'running':
        try:
            process_manager.stop_job(job_id)
            job.status = 'stopped'
            from app import db as app_db
            app_db.session.commit()
            return jsonify({'success': True, 'job': job.to_dict()})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return jsonify({'success': False, 'error': 'Job is not running'}), 400

@bp.route('/api/jobs/<int:job_id>', methods=['GET'])
@require_api_key
def api_get_job(job_id):
    job = CrawlJob.query.get_or_404(job_id)
    return jsonify(job.to_dict())

@bp.route('/api/sites')
@require_api_key
def api_get_sites():
    sites = load_sites_config()
    return jsonify(sites)

@bp.route('/api/sites/country/<country>')
@require_api_key
def api_get_sites_by_country(country):
    sites = get_sites_by_country(country)
    return jsonify(sites)

@bp.route('/api/sites/category/<category>')
@require_api_key
def api_get_sites_by_category(category):
    sites = get_sites_by_category(category)
    return jsonify(sites)

@bp.route('/settings')
def settings():
    config = config_manager.get_all()
    return render_template('settings.html', config=config)

@bp.route('/api/settings', methods=['GET'])
@require_api_key
def api_get_settings():
    return jsonify(config_manager.get_all())

@bp.route('/api/settings', methods=['POST'])
@require_api_key
@validate_json
def api_save_settings():
    data = request.get_json()
    config_manager.update(data)
    return jsonify({'success': True})

@bp.route('/results')
def results():
    # Get all results from database
    results = CrawlResult.query.all()
    jobs = CrawlJob.query.all()
    return render_template('results.html', results=results, jobs=jobs)

@bp.route('/api/results', methods=['GET'])
@require_api_key
def api_get_results():
    results = CrawlResult.query.all()
    return jsonify([result.to_dict() for result in results])

@bp.route('/api/jobs/<int:job_id>', methods=['DELETE'])
@require_api_key
def api_delete_job(job_id):
    job = CrawlJob.query.get_or_404(job_id)
    
    # Stop the job if it's running
    if job.status == 'running':
        try:
            process_manager.stop_job(job_id)
        except:
            pass  # Job might have already finished
    
    from app import db as app_db
    app_db.session.delete(job)
    app_db.session.commit()
    
    return jsonify({'success': True})