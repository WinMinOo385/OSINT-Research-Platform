# OSINT Research Platform

## Overview

The OSINT Research Platform is a comprehensive web application designed for collecting, analyzing, and visualizing Open Source Intelligence (OSINT) data. The platform enables security researchers and investigators to gather information from multiple public sources, organize it into investigations, and analyze patterns across collected data.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python) web framework
- **Database**: SQLAlchemy ORM with SQLite as default database (configurable via DATABASE_URL environment variable)
- **Session Management**: Flask sessions with configurable secret key
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies

### Frontend Architecture  
- **Template Engine**: Jinja2 templates with Flask
- **CSS Framework**: Bootstrap 5 with dark theme
- **JavaScript Libraries**: 
  - D3.js for advanced data visualizations
  - Chart.js for standard charts and graphs
  - Feather Icons for UI icons
- **Fonts**: Inter for UI text, Fira Code for monospace elements

### Data Architecture
- **Primary Models**:
  - `Investigation`: Container for research cases
  - `DataEntry`: Individual pieces of collected OSINT data
  - `AnalysisResult`: Results from automated data analysis
- **Data Storage**: JSON fields for flexible data structure storage
- **Relationships**: One-to-many between investigations and data entries

## Key Components

### OSINT Data Collection (`osint_sources.py`)
- **Purpose**: Collect data from various public sources
- **Supported Sources**: Websites, DNS records, WHOIS data, social media, email analysis, IP analysis
- **Collection Methods**: Web scraping using trafilatura, DNS lookups, API integrations
- **Error Handling**: Graceful degradation with confidence scoring

### Data Analysis Engine (`data_analyzer.py`)
- **Purpose**: Find patterns and relationships in collected data
- **Analysis Types**: Domain clustering, IP correlation, email pattern detection, temporal analysis
- **Pattern Recognition**: Frequency analysis, source reliability scoring, keyword extraction
- **Output**: Structured analysis results for visualization

### Web Interface (`routes.py`)
- **Dashboard**: Overview of investigations and statistics
- **Data Collection**: Interface for configuring and executing OSINT collection
- **Analysis Views**: Visualization and interpretation of collected data
- **Export Functionality**: Data export in multiple formats (CSV, JSON)

## Data Flow

1. **Investigation Creation**: Users create investigation cases to organize research
2. **Target Selection**: Users specify targets (domains, emails, IPs, usernames)
3. **Source Configuration**: Users select which OSINT sources to query
4. **Data Collection**: Platform executes collection from configured sources
5. **Data Storage**: Results stored with metadata and confidence scores
6. **Pattern Analysis**: Automated analysis identifies relationships and patterns
7. **Visualization**: Results presented through interactive charts and tables
8. **Export**: Data can be exported for external analysis or reporting

## External Dependencies

### Python Packages
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and migrations
- **Requests**: HTTP client for web data collection
- **Trafilatura**: Web content extraction and parsing
- **Socket**: Network operations for DNS/IP analysis

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme support
- **D3.js**: Advanced data visualization and interactive charts
- **Chart.js**: Standard chart types and responsive design
- **Feather Icons**: Consistent icon set
- **Google Fonts**: Inter and Fira Code typography

### Optional Integrations
- **Social Media APIs**: For enhanced social media data collection
- **WHOIS Services**: For domain registration information
- **Threat Intelligence APIs**: For enriching collected data

## Deployment Strategy

### Development Environment
- **Local Server**: Flask development server on port 5000
- **Database**: SQLite file-based database for simplicity
- **Debug Mode**: Enabled for development with detailed error reporting

### Production Considerations
- **Database**: Configurable via DATABASE_URL (supports PostgreSQL, MySQL)
- **Session Security**: Environment-based session secret configuration
- **Reverse Proxy**: ProxyFix middleware for nginx/Apache deployment
- **Connection Pooling**: Configured for database connection management
- **Logging**: Structured logging with configurable levels

### Environment Variables
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `SESSION_SECRET`: Session encryption key (defaults to development key)

### Security Features
- **Input Validation**: Form validation and sanitization
- **Error Handling**: Graceful error handling with user-friendly messages
- **Rate Limiting**: Built-in session management for request throttling
- **Data Isolation**: Investigation-based data segregation

The platform is designed to be easily deployable on cloud platforms while maintaining flexibility for local development and testing scenarios.
