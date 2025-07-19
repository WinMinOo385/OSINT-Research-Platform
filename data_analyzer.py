import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import re

class DataAnalyzer:
    """Class for analyzing collected OSINT data and finding patterns"""
    
    def __init__(self):
        pass
    
    def find_patterns(self, data_entries):
        """Find patterns in collected data"""
        try:
            patterns = {
                'common_domains': Counter(),
                'common_ips': Counter(),
                'common_emails': Counter(),
                'source_reliability': {},
                'temporal_patterns': {},
                'content_keywords': Counter()
            }
            
            for entry in data_entries:
                data_dict = entry.get_data_dict()
                
                # Extract domains from various sources
                if entry.source_type == 'website' and entry.source_url:
                    from urllib.parse import urlparse
                    domain = urlparse(entry.source_url).netloc
                    if domain:
                        patterns['common_domains'][domain] += 1
                
                # Extract IPs
                if entry.source_type == 'dns' and 'A' in data_dict:
                    for ip in data_dict['A']:
                        patterns['common_ips'][ip] += 1
                
                # Extract emails
                if 'emails_found' in data_dict:
                    for email in data_dict['emails_found']:
                        patterns['common_emails'][email] += 1
                
                # Source reliability based on confidence scores
                if entry.source_type not in patterns['source_reliability']:
                    patterns['source_reliability'][entry.source_type] = []
                patterns['source_reliability'][entry.source_type].append(entry.confidence_score)
                
                # Temporal patterns
                date_key = entry.collected_at.strftime('%Y-%m-%d')
                if date_key not in patterns['temporal_patterns']:
                    patterns['temporal_patterns'][date_key] = 0
                patterns['temporal_patterns'][date_key] += 1
                
                # Content keywords (from website text)
                if entry.source_type == 'website' and 'text_content' in data_dict:
                    text = data_dict['text_content'].lower()
                    # Extract meaningful words (simplified)
                    words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
                    common_words = ['that', 'this', 'with', 'have', 'will', 'from', 'they', 'been', 'were', 'said', 'each', 'more', 'than', 'many', 'some', 'time', 'very', 'when', 'much', 'new', 'now', 'way', 'may', 'say', 'come', 'its', 'because', 'such', 'through', 'where', 'being', 'how', 'your', 'what', 'their', 'would', 'about', 'which', 'there', 'could', 'should', 'these', 'into', 'just', 'only', 'make', 'know', 'take', 'see', 'him', 'two', 'more', 'go', 'no', 'way', 'could', 'my', 'than', 'first', 'well', 'water', 'been', 'call', 'who', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'has', 'her', 'his', 'had', 'let', 'put', 'say', 'she', 'too', 'old', 'any', 'after', 'move', 'why', 'ask', 'men', 'change', 'went', 'light', 'kind', 'off', 'need', 'house', 'picture', 'try', 'us', 'again', 'animal', 'point', 'mother', 'world', 'near', 'build', 'self', 'earth', 'father', 'head', 'stand', 'own', 'page', 'should', 'country', 'found', 'answer', 'school', 'grow', 'study', 'still', 'learn', 'plant', 'cover', 'food', 'sun', 'four', 'between', 'state', 'keep', 'eye', 'never', 'last', 'let', 'thought', 'city', 'tree', 'cross', 'farm', 'hard', 'start', 'might', 'story', 'saw', 'far', 'sea', 'draw', 'left', 'late', 'run', 'dont', 'while', 'press', 'close', 'night', 'real', 'life', 'few', 'north', 'open', 'seem', 'together', 'next', 'white', 'children', 'begin', 'got', 'walk', 'example', 'ease', 'paper', 'group', 'always', 'music', 'those', 'both', 'mark', 'often', 'letter', 'until', 'mile', 'river', 'car', 'feet', 'care', 'second', 'book', 'carry', 'took', 'science', 'eat', 'room', 'friend', 'began', 'idea', 'fish', 'mountain', 'stop', 'once', 'base', 'hear', 'horse', 'cut', 'sure', 'watch', 'color', 'face', 'wood', 'main', 'enough', 'plain', 'girl', 'usual', 'young', 'ready', 'above', 'ever', 'red', 'list', 'though', 'feel', 'talk', 'bird', 'soon', 'body', 'dog', 'family', 'direct', 'pose', 'leave', 'song', 'measure', 'door', 'product', 'black', 'short', 'numeral', 'class', 'wind', 'question', 'happen', 'complete', 'ship', 'area', 'half', 'rock', 'order', 'fire', 'south', 'problem', 'piece', 'told', 'knew', 'pass', 'since', 'top', 'whole', 'king', 'space', 'heard', 'best', 'hour', 'better', 'during', 'hundred', 'five', 'remember', 'step', 'early', 'hold', 'west', 'ground', 'interest', 'reach', 'fast', 'verb', 'sing', 'listen', 'six', 'table', 'travel', 'less', 'morning', 'ten', 'simple', 'several', 'vowel', 'toward', 'war', 'lay', 'against', 'pattern', 'slow', 'center', 'love', 'person', 'money', 'serve', 'appear', 'road', 'map', 'rain', 'rule', 'govern', 'pull', 'cold', 'notice', 'voice', 'unit', 'power', 'town', 'fine', 'certain', 'fly', 'fall', 'lead', 'cry', 'dark', 'machine', 'note', 'wait', 'plan', 'figure', 'star', 'box', 'noun', 'field', 'rest', 'correct', 'able', 'pound', 'done', 'beauty', 'drive', 'stood', 'contain', 'front', 'teach', 'week', 'final', 'gave', 'green', 'oh', 'quick', 'develop', 'ocean', 'warm', 'free', 'minute', 'strong', 'special', 'mind', 'behind', 'clear', 'tail', 'produce', 'fact', 'street', 'inch', 'multiply', 'nothing', 'course', 'stay', 'wheel', 'full', 'force', 'blue', 'object', 'decide', 'surface', 'deep', 'moon', 'island', 'foot', 'system', 'busy', 'test', 'record', 'boat', 'common', 'gold', 'possible', 'plane', 'stead', 'dry', 'wonder', 'laugh', 'thousands', 'ago', 'ran', 'check', 'game', 'shape', 'equate', 'hot', 'miss', 'brought', 'heat', 'snow', 'tire', 'bring', 'yes', 'distant', 'fill', 'east', 'paint', 'language', 'among']
                    filtered_words = [word for word in words if word not in common_words and len(word) > 3]
                    for word in filtered_words[:20]:  # Top 20 words per document
                        patterns['content_keywords'][word] += 1
            
            # Calculate average reliability by source
            for source_type, scores in patterns['source_reliability'].items():
                patterns['source_reliability'][source_type] = {
                    'average_confidence': sum(scores) / len(scores),
                    'total_entries': len(scores),
                    'min_confidence': min(scores),
                    'max_confidence': max(scores)
                }
            
            return {
                'patterns': {
                    'top_domains': dict(patterns['common_domains'].most_common(10)),
                    'top_ips': dict(patterns['common_ips'].most_common(10)),
                    'top_emails': dict(patterns['common_emails'].most_common(10)),
                    'source_reliability': patterns['source_reliability'],
                    'temporal_distribution': patterns['temporal_patterns'],
                    'top_keywords': dict(patterns['content_keywords'].most_common(20))
                },
                'confidence': 0.8,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'confidence': 0.0,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
    
    def find_correlations(self, data_entries):
        """Find correlations between different data points"""
        try:
            correlations = {
                'domain_ip_mapping': defaultdict(set),
                'email_domain_mapping': defaultdict(set),
                'temporal_correlations': defaultdict(list),
                'cross_source_validation': {}
            }
            
            # Group entries by target for cross-validation
            target_groups = defaultdict(list)
            for entry in data_entries:
                target_groups[entry.target].append(entry)
            
            for target, entries in target_groups.items():
                if len(entries) > 1:
                    source_types = [entry.source_type for entry in entries]
                    correlations['cross_source_validation'][target] = {
                        'sources_used': source_types,
                        'source_count': len(set(source_types)),
                        'total_entries': len(entries),
                        'confidence_scores': [entry.confidence_score for entry in entries],
                        'avg_confidence': sum([entry.confidence_score for entry in entries]) / len(entries)
                    }
            
            # Find domain-IP correlations
            for entry in data_entries:
                data_dict = entry.get_data_dict()
                
                if entry.source_type == 'dns' and 'A' in data_dict:
                    domain = entry.target
                    for ip in data_dict['A']:
                        correlations['domain_ip_mapping'][domain].add(ip)
                
                if entry.source_type == 'website' and 'emails_found' in data_dict:
                    from urllib.parse import urlparse
                    if entry.source_url:
                        domain = urlparse(entry.source_url).netloc
                        for email in data_dict['emails_found']:
                            email_domain = email.split('@')[1] if '@' in email else ''
                            if email_domain:
                                correlations['email_domain_mapping'][domain].add(email_domain)
                
                # Temporal correlations
                hour = entry.collected_at.hour
                correlations['temporal_correlations'][entry.source_type].append(hour)
            
            # Convert sets to lists for JSON serialization
            for domain in correlations['domain_ip_mapping']:
                correlations['domain_ip_mapping'][domain] = list(correlations['domain_ip_mapping'][domain])
            
            for domain in correlations['email_domain_mapping']:
                correlations['email_domain_mapping'][domain] = list(correlations['email_domain_mapping'][domain])
            
            return {
                'correlations': dict(correlations),
                'confidence': 0.7,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'confidence': 0.0,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
    
    def create_timeline(self, data_entries):
        """Create a timeline of data collection activities"""
        try:
            timeline_events = []
            
            for entry in data_entries:
                timeline_events.append({
                    'timestamp': entry.collected_at.isoformat(),
                    'date': entry.collected_at.strftime('%Y-%m-%d'),
                    'time': entry.collected_at.strftime('%H:%M:%S'),
                    'source_type': entry.source_type,
                    'target': entry.target,
                    'confidence': entry.confidence_score,
                    'data_size': len(str(entry.get_data_dict())),
                    'has_error': 'error' in entry.get_data_dict()
                })
            
            # Sort by timestamp
            timeline_events.sort(key=lambda x: x['timestamp'])
            
            # Create daily summaries
            daily_summary = defaultdict(lambda: {
                'total_collections': 0,
                'source_types': set(),
                'avg_confidence': 0,
                'total_data_size': 0,
                'errors': 0
            })
            
            for event in timeline_events:
                date = event['date']
                daily_summary[date]['total_collections'] += 1
                daily_summary[date]['source_types'].add(event['source_type'])
                daily_summary[date]['avg_confidence'] += event['confidence']
                daily_summary[date]['total_data_size'] += event['data_size']
                if event['has_error']:
                    daily_summary[date]['errors'] += 1
            
            # Calculate averages and convert sets to lists
            for date in daily_summary:
                summary = daily_summary[date]
                summary['avg_confidence'] = summary['avg_confidence'] / summary['total_collections']
                summary['source_types'] = list(summary['source_types'])
                summary['unique_sources'] = len(summary['source_types'])
            
            return {
                'timeline': {
                    'events': timeline_events,
                    'daily_summary': dict(daily_summary),
                    'total_events': len(timeline_events),
                    'date_range': {
                        'start': timeline_events[0]['date'] if timeline_events else None,
                        'end': timeline_events[-1]['date'] if timeline_events else None
                    }
                },
                'confidence': 0.9,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'confidence': 0.0,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
