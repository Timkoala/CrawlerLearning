from flask import Blueprint, render_template, request, redirect, url_for, jsonify, Response
from models.job import CrawlJob, CrawlResult, CrawlRun
from crawler.process_manager import ProcessManager
from config.config_manager import ConfigManager
from config.sites_config import load_sites_config, get_sites_by_country, get_sites_by_category
from web.auth import require_api_key, validate_json
import json
import csv
import io

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
    # Merge live engine status
    engine_status = process_manager.get_job_status(job_id)
    updated = False
    if engine_status in ('running', 'completed', 'finished'):
        if job.status != engine_status:
            job.status = engine_status
            updated = True
    elif engine_status == 'not_found' and job.status == 'running':
        job.status = 'finished'
        updated = True
    if updated:
        from app import db as app_db
        app_db.session.commit()
    return jsonify(job.to_dict())

@bp.route('/api/jobs/<int:job_id>', methods=['PUT'])
@require_api_key
@validate_json
def api_update_job(job_id):
    job = CrawlJob.query.get_or_404(job_id)
    data = request.get_json()
    if not data.get('name') or not data.get('target_url'):
        return jsonify({'success': False, 'error': 'Name and target_url are required'}), 400
    job.name = data['name']
    job.target_url = data['target_url']
    job.max_depth = data.get('max_depth', job.max_depth)
    if data.get('custom_rules'):
        job.custom_rules = json.dumps(data['custom_rules'])
    else:
        job.custom_rules = None
    from app import db as app_db
    app_db.session.commit()
    return jsonify({'success': True, 'job': job.to_dict()})

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
    # Keep server-rendered page simple; data is loaded via API
    jobs = CrawlJob.query.all()
    return render_template('results.html', jobs=jobs)

@bp.route('/api/runs', methods=['GET'])
@require_api_key
def api_get_runs():
    job_id = request.args.get('job_id')
    q = CrawlRun.query
    if job_id:
        try:
            q = q.filter(CrawlRun.job_id == int(job_id))
        except Exception:
            pass
    runs = q.order_by(CrawlRun.started_at.desc()).all()
    return jsonify([r.to_dict() for r in runs])

@bp.route('/api/results', methods=['GET'])
@require_api_key
def api_get_results():
    try:
        page = int(request.args.get('page', 1))
    except Exception:
        page = 1
    try:
        page_size = int(request.args.get('page_size', 20))
    except Exception:
        page_size = 20
    job_id = request.args.get('job_id')
    run_id = request.args.get('run_id')
    q = request.args.get('q', '').strip()

    query = CrawlResult.query
    if job_id:
        try:
            query = query.filter(CrawlResult.job_id == int(job_id))
        except Exception:
            pass
    if run_id:
        try:
            query = query.filter(CrawlResult.run_id == int(run_id))
        except Exception:
            pass
    if q:
        like_pattern = f"%{q}%"
        query = query.filter((CrawlResult.title.ilike(like_pattern)) | (CrawlResult.content.ilike(like_pattern)))

    total = query.count()
    items = (query.order_by(CrawlResult.scraped_at.desc()).offset((page - 1) * page_size).limit(page_size).all())
    return jsonify({'total': total, 'page': page, 'page_size': page_size, 'items': [item.to_dict() for item in items]})

@bp.route('/api/results/export', methods=['GET'])
@require_api_key
def api_export_results():
    fmt = request.args.get('format', 'json').lower()
    job_id = request.args.get('job_id')
    run_id = request.args.get('run_id')
    q = request.args.get('q', '').strip()

    query = CrawlResult.query
    if job_id:
        try:
            query = query.filter(CrawlResult.job_id == int(job_id))
        except Exception:
            pass
    if run_id:
        try:
            query = query.filter(CrawlResult.run_id == int(run_id))
        except Exception:
            pass
    if q:
        like_pattern = f"%{q}%"
        query = query.filter(
            (CrawlResult.title.ilike(like_pattern)) | (CrawlResult.content.ilike(like_pattern))
        )

    items = query.order_by(CrawlResult.scraped_at.desc()).all()

    if fmt == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['id','job_id','run_id','url','title','content','scraped_at'])
        for it in items:
            d = it.to_dict()
            writer.writerow([d.get('id'), d.get('job_id'), d.get('run_id'), d.get('url'), d.get('title') or '', (d.get('content') or '').replace('\n',' ').replace('\r',' '), d.get('scraped_at') or ''])
        csv_data = output.getvalue()
        return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename="results.csv"'})
    else:
        # default json
        return jsonify([it.to_dict() for it in items])

@bp.route('/api/results/<int:result_id>', methods=['DELETE'])
@require_api_key
def api_delete_result(result_id):
    result = CrawlResult.query.get_or_404(result_id)
    from app import db as app_db
    app_db.session.delete(result)
    app_db.session.commit()
    return jsonify({'success': True})

@bp.route('/api/results/batch_delete', methods=['POST'])
@require_api_key
@validate_json
def api_results_batch_delete():
    data = request.get_json() or {}
    ids = data.get('ids') or []
    run_id = data.get('run_id')
    from app import db as app_db
    deleted = 0
    if ids:
        for rid in ids:
            item = CrawlResult.query.get(rid)
            if item:
                app_db.session.delete(item)
                deleted += 1
        app_db.session.commit()
        return jsonify({'success': True, 'deleted': deleted})
    if run_id:
        run_id_int = int(run_id)
        q = CrawlResult.query.filter(CrawlResult.run_id == run_id_int)
        count = q.count()
        q.delete(synchronize_session=False)
        # 同时删除批次记录
        run = CrawlRun.query.get(run_id_int)
        if run:
            app_db.session.delete(run)
        app_db.session.commit()
        return jsonify({'success': True, 'deleted': count, 'run_deleted': True})
    return jsonify({'success': False, 'error': 'No ids or run_id provided'}), 400

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