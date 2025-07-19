from flask import render_template, request, redirect, url_for, flash, jsonify, make_response
from app import app, db
from models import Investigation, DataEntry, AnalysisResult
from osint_sources import OSINTCollector
from data_analyzer import DataAnalyzer
import json
import csv
import io
from datetime import datetime

@app.route('/')
def dashboard():
    """Main dashboard showing investigations and recent activity"""
    investigations = Investigation.query.order_by(Investigation.updated_at.desc()).limit(10).all()
    recent_data = DataEntry.query.order_by(DataEntry.collected_at.desc()).limit(20).all()
    
    # Get statistics for dashboard
    total_investigations = Investigation.query.count()
    total_data_entries = DataEntry.query.count()
    active_investigations = Investigation.query.filter_by(status='active').count()
    
    stats = {
        'total_investigations': total_investigations,
        'total_data_entries': total_data_entries,
        'active_investigations': active_investigations,
        'data_sources': len(set([entry.source_type for entry in DataEntry.query.all()]))
    }
    
    return render_template('dashboard.html', 
                         investigations=investigations, 
                         recent_data=recent_data,
                         stats=stats)

@app.route('/search')
def search():
    """Search interface for OSINT data collection"""
    investigations = Investigation.query.filter_by(status='active').all()
    return render_template('search.html', investigations=investigations)

@app.route('/collect_data', methods=['POST'])
def collect_data():
    """Endpoint for collecting OSINT data"""
    try:
        investigation_id = request.form.get('investigation_id')
        target = request.form.get('target')
        source_types = request.form.getlist('source_types')
        
        if not investigation_id or not target or not source_types:
            flash('All fields are required', 'danger')
            return redirect(url_for('search'))
        
        investigation = Investigation.query.get_or_404(investigation_id)
        collector = OSINTCollector()
        
        collected_count = 0
        for source_type in source_types:
            try:
                data = collector.collect_data(source_type, target)
                if data:
                    entry = DataEntry(
                        investigation_id=investigation_id,
                        source_type=source_type,
                        target=target,
                        source_url=data.get('source_url', ''),
                        confidence_score=data.get('confidence_score', 0.0)
                    )
                    entry.set_data_dict(data.get('data', {}))
                    entry.set_metadata_dict(data.get('metadata', {}))
                    
                    db.session.add(entry)
                    collected_count += 1
            except Exception as e:
                app.logger.error(f"Error collecting from {source_type}: {str(e)}")
                continue
        
        if collected_count > 0:
            # Update investigation timestamp
            investigation.updated_at = datetime.utcnow()
            db.session.commit()
            flash(f'Successfully collected data from {collected_count} sources', 'success')
        else:
            flash('No data could be collected from the specified sources', 'warning')
        
        return redirect(url_for('view_investigation', id=investigation_id))
        
    except Exception as e:
        app.logger.error(f"Error in collect_data: {str(e)}")
        flash('An error occurred while collecting data', 'danger')
        return redirect(url_for('search'))

@app.route('/investigation/<int:id>')
def view_investigation(id):
    """View specific investigation with all collected data"""
    investigation = Investigation.query.get_or_404(id)
    data_entries = DataEntry.query.filter_by(investigation_id=id).order_by(DataEntry.collected_at.desc()).all()
    analysis_results = AnalysisResult.query.filter_by(investigation_id=id).order_by(AnalysisResult.created_at.desc()).all()
    
    # Group data by source type for better visualization
    data_by_source = {}
    for entry in data_entries:
        if entry.source_type not in data_by_source:
            data_by_source[entry.source_type] = []
        data_by_source[entry.source_type].append(entry)
    
    return render_template('analysis.html', 
                         investigation=investigation,
                         data_entries=data_entries,
                         data_by_source=data_by_source,
                         analysis_results=analysis_results)

@app.route('/create_investigation', methods=['POST'])
def create_investigation():
    """Create a new investigation"""
    try:
        name = request.form.get('name')
        description = request.form.get('description', '')
        
        if not name:
            flash('Investigation name is required', 'danger')
            return redirect(url_for('dashboard'))
        
        investigation = Investigation(name=name, description=description)
        db.session.add(investigation)
        db.session.commit()
        
        flash('Investigation created successfully', 'success')
        return redirect(url_for('view_investigation', id=investigation.id))
        
    except Exception as e:
        app.logger.error(f"Error creating investigation: {str(e)}")
        flash('An error occurred while creating the investigation', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/analyze/<int:investigation_id>')
def analyze_investigation(investigation_id):
    """Run analysis on investigation data"""
    try:
        investigation = Investigation.query.get_or_404(investigation_id)
        data_entries = DataEntry.query.filter_by(investigation_id=investigation_id).all()
        
        if not data_entries:
            flash('No data available for analysis', 'warning')
            return redirect(url_for('view_investigation', id=investigation_id))
        
        analyzer = DataAnalyzer()
        
        # Run different types of analysis
        pattern_analysis = analyzer.find_patterns(data_entries)
        correlation_analysis = analyzer.find_correlations(data_entries)
        timeline_analysis = analyzer.create_timeline(data_entries)
        
        # Save analysis results
        analyses = [
            ('pattern', 'Pattern Analysis', pattern_analysis),
            ('correlation', 'Correlation Analysis', correlation_analysis),
            ('timeline', 'Timeline Analysis', timeline_analysis)
        ]
        
        for analysis_type, title, results in analyses:
            if results:
                analysis_result = AnalysisResult(
                    investigation_id=investigation_id,
                    analysis_type=analysis_type,
                    title=title,
                    description=f"Automated {title.lower()} of collected data",
                    confidence=results.get('confidence', 0.0)
                )
                analysis_result.set_results_dict(results)
                db.session.add(analysis_result)
        
        db.session.commit()
        flash('Analysis completed successfully', 'success')
        
    except Exception as e:
        app.logger.error(f"Error analyzing investigation: {str(e)}")
        flash('An error occurred during analysis', 'danger')
    
    return redirect(url_for('view_investigation', id=investigation_id))

@app.route('/export')
def export_page():
    """Export interface"""
    investigations = Investigation.query.all()
    return render_template('export.html', investigations=investigations)

@app.route('/export_data/<int:investigation_id>/<format>')
def export_data(investigation_id, format):
    """Export investigation data in specified format"""
    try:
        investigation = Investigation.query.get_or_404(investigation_id)
        data_entries = DataEntry.query.filter_by(investigation_id=investigation_id).all()
        
        if format == 'json':
            export_data = {
                'investigation': {
                    'id': investigation.id,
                    'name': investigation.name,
                    'description': investigation.description,
                    'created_at': investigation.created_at.isoformat(),
                    'updated_at': investigation.updated_at.isoformat()
                },
                'data_entries': []
            }
            
            for entry in data_entries:
                export_data['data_entries'].append({
                    'id': entry.id,
                    'source_type': entry.source_type,
                    'source_url': entry.source_url,
                    'target': entry.target,
                    'data': entry.get_data_dict(),
                    'metadata': entry.get_metadata_dict(),
                    'collected_at': entry.collected_at.isoformat(),
                    'confidence_score': entry.confidence_score
                })
            
            response = make_response(json.dumps(export_data, indent=2))
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = f'attachment; filename={investigation.name}_data.json'
            
        elif format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(['ID', 'Source Type', 'Target', 'Source URL', 'Collected At', 'Confidence Score', 'Data Summary'])
            
            # Write data
            for entry in data_entries:
                data_dict = entry.get_data_dict()
                data_summary = str(data_dict)[:100] + '...' if len(str(data_dict)) > 100 else str(data_dict)
                writer.writerow([
                    entry.id,
                    entry.source_type,
                    entry.target,
                    entry.source_url,
                    entry.collected_at.strftime('%Y-%m-%d %H:%M:%S'),
                    entry.confidence_score,
                    data_summary
                ])
            
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename={investigation.name}_data.csv'
        
        else:
            flash('Invalid export format', 'danger')
            return redirect(url_for('export_page'))
        
        return response
        
    except Exception as e:
        app.logger.error(f"Error exporting data: {str(e)}")
        flash('An error occurred during export', 'danger')
        return redirect(url_for('export_page'))

@app.route('/api/visualization_data/<int:investigation_id>')
def get_visualization_data(investigation_id):
    """API endpoint for visualization data"""
    try:
        data_entries = DataEntry.query.filter_by(investigation_id=investigation_id).all()
        
        # Prepare data for different visualization types
        source_distribution = {}
        timeline_data = []
        confidence_data = []
        
        for entry in data_entries:
            # Source distribution
            if entry.source_type not in source_distribution:
                source_distribution[entry.source_type] = 0
            source_distribution[entry.source_type] += 1
            
            # Timeline data
            timeline_data.append({
                'date': entry.collected_at.strftime('%Y-%m-%d'),
                'source_type': entry.source_type,
                'target': entry.target,
                'confidence': entry.confidence_score
            })
            
            # Confidence data
            confidence_data.append({
                'source_type': entry.source_type,
                'confidence': entry.confidence_score,
                'target': entry.target
            })
        
        return jsonify({
            'source_distribution': source_distribution,
            'timeline_data': timeline_data,
            'confidence_data': confidence_data
        })
        
    except Exception as e:
        app.logger.error(f"Error getting visualization data: {str(e)}")
        return jsonify({'error': 'Failed to load visualization data'}), 500
