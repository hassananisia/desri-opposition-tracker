# DESRI Public Engagement Intelligence Hub

An internal tool for tracking and managing community opposition to renewable energy projects across the United States.

## 🎯 Features

### Opposition Tracker
- Interactive map showing projects facing opposition
- Filter by state, county, type, and status
- Add and manage project data
- Document community survey responses

### 2025 Opposition Report
- Statistical analysis and visualizations
- Track opposition trends and outcomes
- Identify key concerns and patterns
- Competitive intelligence

### Public Hearings Resources
- Searchable Q&A database
- DESRI-approved responses for common concerns
- Custom topic management
- Soft delete with recovery options

## 🚀 Quick Start

This application is deployed on Streamlit Community Cloud for authorized DESRI users.

### Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```
4. Run the application:
   ```bash
   streamlit run desri_hub_app.py
   ```

## 📁 Project Structure

```
desri-opposition-tracker/
├── desri_hub_app.py           # Main application file
├── supabase_config.py          # Database configuration
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore file
├── .env                        # Environment variables (local only)
├── data/                       # Data files
│   └── *.csv                   # CSV data files
└── docs/                       # Documentation
    ├── USER_GUIDE.md          # User guide
    └── DEPLOYMENT_GUIDE.md    # Deployment instructions
```

## 🔒 Security

- Environment variables stored in `.env` (never committed)
- Supabase for secure database operations
- Row Level Security (RLS) configured
- Private repository recommended

## 📊 Data Sources

- Opposition Tracker Data (June 2025)
- County-level data for all US states
- User-contributed project data
- Community survey responses

## 🛠️ Technologies

- **Frontend**: Streamlit
- **Database**: Supabase (PostgreSQL)
- **Mapping**: Folium
- **Charts**: Plotly
- **Deployment**: Streamlit Community Cloud

## 📖 Documentation

- [User Guide](USER_GUIDE.md) - Complete user instructions
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Deployment instructions

## ⚠️ Important Notes

### County Format
When searching or entering county data, always use the format: `[Name] County`
- ✅ Correct: "Los Angeles County"
- ❌ Incorrect: "Los Angeles"

### Database Setup
Before first use, ensure the Supabase database has:
1. `public_hearing_qa` table with `is_removed` column
2. Proper RLS policies configured
3. Required tables created

## 🤝 Support

For technical issues:
1. Check the User Guide
2. Review error logs
3. Verify database connection
4. Clear browser cache

## 📄 License

© 2025 DESRI - Internal Use Only

---

*Last Updated: January 2025*