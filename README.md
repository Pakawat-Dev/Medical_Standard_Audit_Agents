# Medical Software Audit Agents 🏥

AI-powered audit team for medical device compliance with ISO 13485:2016, ISO 14971:2019, and IEC 62304:2006 standards.

## Features

- **Multi-Agent Audit Team**: Specialized AI agents for different compliance areas
- **Interactive Web Interface**: Streamlit-based UI for easy interaction
- **Comprehensive Standards Coverage**: ISO 13485, ISO 14971, and IEC 62304
- **Thai Translation**: Automatic translation of audit reports

## Audit Team

| Agent | Specialization | Standards |
|-------|---------------|-----------|
| **QMS Agent** | Quality Management System, Risk Management | ISO 13485:2016, ISO 14971:2019 |
| **HR Agent** | Resource Management, Purchasing | ISO 13485:2016 |
| **Engineer Agent** | Design Controls, Software Lifecycle | ISO 13485:2016, IEC 62304:2006 |
| **Lead Auditor** | Summary Reports, Thai Translation | All Standards |

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   Create `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run Streamlit App**
   ```bash
   streamlit run audit_agents_streamlit.py
   ```

4. **Access Web Interface**
   Open your browser to `http://localhost:8501`

## Usage

1. Select a predefined audit topic or enter a custom query
2. Click "Start Audit" to run the AI agent team
3. Review findings from each specialized agent
4. Get comprehensive audit summary with Thai translation

## Requirements

- Python 3.8+
- OpenAI API key
- Dependencies listed in `requirements.txt`

## Standards Compliance

- **ISO 13485:2016** - Medical Device Quality Management Systems
- **ISO 14971:2019** - Risk Management for Medical Devices  
- **IEC 62304:2006** - Medical Device Software Lifecycle Processes
