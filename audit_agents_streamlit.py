import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo, ModelFamily
from autogen_agentchat.agents import AssistantAgent, SocietyOfMindAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import ChatMessage
import json
from io import StringIO
import sys

class StreamlitCapture:
    def __init__(self):
        self.messages = []
    
    def write(self, text):
        if text.strip():
            self.messages.append(text)
    
    def flush(self):
        pass

async def run_audit_agents(task):
    load_dotenv()
    
    model_client_openai = OpenAIChatCompletionClient(
        model="gpt-5-mini",
        api_key=os.environ["OPENAI_API_KEY"],
        model_info=ModelInfo(
            vision=True,
            function_calling=True,
            json_output=True,
            family=ModelFamily.GPT_5,
        )
    )

    QMS_agent = AssistantAgent(
        name="QMS_agent",
        model_client=model_client_openai,
        system_message="""
        You are an ISO 13485:2016 and ISO 14971:2019 Auditor. 
        role is to evaluate, question, and verify compliance with medical device quality management and risk management standards. 

        Focus particularly on:
        - ISO 13485:2016 Clause 4 (Quality Management System),
        - ISO 13485:2016 Clause 5 (Management Responsibility),
        - ISO 13485:2016 Clause 8 (Measurement, Analysis, and Improvement),
        - ISO 14971:2019 requirements for risk management throughout the product lifecycle.

        Behave like a professional auditor:
        - Ask probing, compliance-focused questions.  
        - Identify gaps, risks, or nonconformities with supporting evidence.  
        - Provide clear, evidence-based observations.  
        - Reference the relevant clauses in ISO 13485:2016 and ISO 14971:2019.  
        - Write in a formal, precise, and objective tone suitable for audit reporting.  
        """
        )

    HR_agent = AssistantAgent(
        name="HR_agent",
        model_client=model_client_openai,
        system_message="""
        You are an ISO 13485:2016 auditor with deep knowledge of medical device quality management systems. 
        Your focus is on Clause 6 (Resource Management) and Clause 7.4 (Purchasing).
    
        - For Clause 6, evaluate whether organizations provide adequate resources, competence, training, infrastructure, and work environment to ensure product conformity and QMS effectiveness. 
        - For Clause 7.4, review supplier evaluation, selection, monitoring, and control processes, ensuring they meet regulatory and customer requirements.
    
        When responding:
        - Write clearly and professionally in the style of an experienced auditor.
        - Reference relevant ISO 13485:2016 requirements when necessary.
        - Identify gaps, risks, or areas of nonconformance with practical recommendations.
        """
        )

    Engineer_agent = AssistantAgent(
        name="Engineer_agent",
        model_client=model_client_openai,
        system_message="""
        You are an ISO 13485:2016 and IEC 62304:2006 auditor specializing in technical and engineering aspects of medical device development, with expertise in medical device software lifecycle processes.
        
        Your focus areas include:
        - ISO 13485:2016 Clause 7.3 (Design and Development) and technical compliance requirements
        - IEC 62304:2006 medical device software lifecycle processes and safety classification
        
        For ISO 13485:2016:
        - Evaluate design controls, design inputs/outputs, design review, verification, validation, and design transfer processes
        - Assess technical documentation, design history files, and engineering change control procedures
        - Review risk management integration within design and development processes per ISO 14971:2019
        
        For IEC 62304:2006:
        - Audit software safety classification (Class A, B, C) and associated requirements
        - Evaluate software development planning, requirements analysis, architectural design, and detailed design
        - Review software implementation, integration testing, system testing, and software release processes
        - Assess software configuration management, problem resolution, and software maintenance processes
        - Verify software risk management activities and their integration with overall device risk management
        - Examine software of unknown provenance (SOUP) evaluation and management
        
        When responding:
        - Apply engineering and software development expertise to identify technical compliance gaps
        - Reference relevant ISO 13485:2016 design control requirements and IEC 62304:2006 clauses
        - Focus on both hardware and software technical documentation adequacy and process effectiveness
        - Provide engineering-focused audit observations with specific recommendations for software lifecycle compliance
        - Address software safety classification appropriateness and associated documentation requirements
        """
        )

    Lead_auditor = AssistantAgent(
        name="Lead_auditor",
        model_client=model_client_openai,
        system_message="""
        You are the Lead Auditor with comprehensive expertise in ISO 13485:2016, ISO 14971:2019, and IEC 62304:2006 standards for medical device quality management, risk management, and software lifecycle processes.
        
        Your primary responsibilities:
        1. Review and synthesize findings from the audit team (QMS_agent, HR_agent, Engineer_agent)
        2. Create comprehensive audit summary reports
        3. Translate final audit reports to Thai language
        
        Standards Expertise:
        - ISO 13485:2016: Complete knowledge of all clauses including QMS requirements, management responsibility, resource management, product realization, and measurement/analysis/improvement
        - ISO 14971:2019: Risk management application throughout medical device lifecycle, risk analysis, evaluation, control, and post-market surveillance
        - IEC 62304:2006: Medical device software lifecycle processes, safety classification, development planning, implementation, and maintenance
        
        When creating audit summaries:
        - Consolidate findings from all team members into a coherent audit report
        - Identify cross-functional compliance gaps and systemic issues
        - Prioritize findings by risk level and regulatory impact
        - Provide executive-level recommendations for corrective actions
        - Ensure all findings reference appropriate standard clauses
        - Structure reports with clear sections: Executive Summary, Findings, Recommendations, Conclusion
        
        Translation Requirements:
        - Translate the complete audit summary report to Thai language
        - Maintain technical accuracy of regulatory terminology
        - Preserve the formal audit report structure and tone
        - Ensure Thai translation is professional and suitable for regulatory submission
        
        Write in a senior auditor's authoritative yet professional tone, demonstrating deep regulatory knowledge and leadership experience.
        """
    )

    termination = TextMentionTermination(text="APPROVE") | MaxMessageTermination(max_messages=10)
    
    team = RoundRobinGroupChat(
        participants=[QMS_agent, HR_agent, Engineer_agent],
        termination_condition=termination,
    )

    society_of_mind_agent = SocietyOfMindAgent(
        name="society_of_mind", 
        team=team,
        model_client=model_client_openai,
    )
    
    final_team = RoundRobinGroupChat(
        participants=[society_of_mind_agent, Lead_auditor],
        max_turns=2,
    )

    # Collect messages from the stream
    messages = []
    async for message in final_team.run_stream(task=task):
        messages.append(message)
    
    return messages

def main():
    st.set_page_config(
        page_title="Medical Device Audit Agents",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 Medical Device Audit Agents")
    st.markdown("**AI-Powered Audit Team for ISO 13485:2016, ISO 14971:2019, and IEC 62304:2006**")
    
    # Sidebar with agent information
    with st.sidebar:
        st.header("🤖 Audit Team")
        st.markdown("""
        **QMS Agent** - ISO 13485:2016 & ISO 14971:2019
        - Quality Management System
        - Management Responsibility  
        - Risk Management
        
        **HR Agent** - ISO 13485:2016
        - Resource Management (Clause 6)
        - Purchasing (Clause 7.4)
        
        **Engineer Agent** - ISO 13485:2016 & IEC 62304:2006
        - Design & Development (Clause 7.3)
        - Software Lifecycle Processes
        
        **Lead Auditor** - All Standards
        - Audit Summary & Reporting
        - Thai Translation
        """)
    
    # Main interface
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📝 Audit Query")
        
        # Predefined audit topics
        audit_topics = [
            "Tell me about document required for human resources.",
            "Evaluate design control processes and documentation.",
            "Review software safety classification requirements.",
            "Assess risk management implementation.",
            "Audit supplier evaluation and control processes.",
            "Review quality management system effectiveness.",
            "Custom query..."
        ]
        
        selected_topic = st.selectbox("Select audit topic:", audit_topics)
        
        if selected_topic == "Custom query...":
            custom_query = st.text_area("Enter your custom audit query:", height=100)
            task = custom_query if custom_query else "Tell me about document required for human resources."
        else:
            task = selected_topic
        
        run_audit = st.button("🚀 Start Audit", type="primary")
    
    with col2:
        st.subheader("📊 Audit Results")
        
        if run_audit and task:
            with st.spinner("Running audit agents..."):
                try:
                    # Run the audit agents
                    messages = asyncio.run(run_audit_agents(task))
                    
                    # Display results
                    if messages:
                        for i, message in enumerate(messages):
                            if hasattr(message, 'source') and hasattr(message, 'content'):
                                agent_name = message.source
                                content = message.content
                                
                                # Create expandable sections for each agent
                                with st.expander(f"💬 {agent_name}", expanded=True):
                                    st.markdown(content)
                            else:
                                st.write(f"Message {i+1}: {message}")
                    else:
                        st.warning("No messages received from agents.")
                        
                except Exception as e:
                    st.error(f"Error running audit agents: {str(e)}")
        
        elif not task:
            st.info("Please enter an audit query to begin.")
    
    # Footer
    st.markdown("---")
    st.markdown("*Medical Device Audit Agents - Powered by OpenAI GPT-5*")

if __name__ == "__main__":
    main()