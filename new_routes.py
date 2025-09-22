@bp.route('/api/jobs/<int:job_id>', methods=['GET'])
@require_api_key
def api_get_job(job_id):
    job = CrawlJob.query.get_or_404(job_id)
    return jsonify(job.to_dict())

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