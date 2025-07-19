from app import db
from datetime import datetime
import json

class Investigation(db.Model):
    """Model for storing investigation cases"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(50), default='active')
    
    # Relationship to data entries
    data_entries = db.relationship('DataEntry', backref='investigation', lazy=True, cascade='all, delete-orphan')

class DataEntry(db.Model):
    """Model for storing collected OSINT data"""
    id = db.Column(db.Integer, primary_key=True)
    investigation_id = db.Column(db.Integer, db.ForeignKey('investigation.id'), nullable=False)
    source_type = db.Column(db.String(100), nullable=False)  # 'website', 'social_media', 'dns', etc.
    source_url = db.Column(db.String(500))
    target = db.Column(db.String(200), nullable=False)  # Search target/query
    data = db.Column(db.Text)  # JSON string of collected data
    meta_data = db.Column(db.Text)  # JSON string of metadata
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)
    confidence_score = db.Column(db.Float, default=0.0)
    
    def get_data_dict(self):
        """Parse JSON data string to dictionary"""
        try:
            return json.loads(self.data) if self.data else {}
        except json.JSONDecodeError:
            return {}
    
    def set_data_dict(self, data_dict):
        """Convert dictionary to JSON string"""
        self.data = json.dumps(data_dict)
    
    def get_metadata_dict(self):
        """Parse JSON metadata string to dictionary"""
        try:
            return json.loads(self.meta_data) if self.meta_data else {}
        except json.JSONDecodeError:
            return {}
    
    def set_metadata_dict(self, metadata_dict):
        """Convert dictionary to JSON string"""
        self.meta_data = json.dumps(metadata_dict)

class AnalysisResult(db.Model):
    """Model for storing analysis results and patterns"""
    id = db.Column(db.Integer, primary_key=True)
    investigation_id = db.Column(db.Integer, db.ForeignKey('investigation.id'), nullable=False)
    analysis_type = db.Column(db.String(100), nullable=False)  # 'pattern', 'correlation', 'timeline'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    results = db.Column(db.Text)  # JSON string of analysis results
    confidence = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_results_dict(self):
        """Parse JSON results string to dictionary"""
        try:
            return json.loads(self.results) if self.results else {}
        except json.JSONDecodeError:
            return {}
    
    def set_results_dict(self, results_dict):
        """Convert dictionary to JSON string"""
        self.results = json.dumps(results_dict)
