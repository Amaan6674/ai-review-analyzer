import streamlit as st
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from typing import TypedDict, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Review Analyzer",
    page_icon="⭐",
    layout="centered"
)

# Initialize session state
if 'workflow' not in st.session_state:
    # Initialize model
    model = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3,
    )
    
    # Define schemas
    class SentimentSchema(BaseModel):
        sentiment: Literal["positive", "negative"] = Field(description='Sentiment of the review')
    
    class DiagnosisSchema(BaseModel):
        issue_type: Literal["UX", "Performance", "Bug", "Support", "Other"] = Field(description='The category of issue mentioned in the review')
        tone: Literal["angry", "frustrated", "disappointed", "calm"] = Field(description='The emotional tone expressed by the user')
        urgency: Literal["low", "medium", "high"] = Field(description='How urgent or critical the issue appears to be')
    
    # Create structured models
    structured_model = model.with_structured_output(SentimentSchema)
    structured_model2 = model.with_structured_output(DiagnosisSchema)
    
    # Define state
    class ReviewState(TypedDict):
        review: str
        sentiment: Literal["positive", "negative"]
        diagnosis: dict
        response: str
    
    # Define workflow functions
    def find_sentiment(state: ReviewState):
        prompt = f'For the following review find out the sentiment \n {state["review"]}'
        sentiment = structured_model.invoke(prompt).sentiment
        return {'sentiment': sentiment}
    
    def check_sentiment(state: ReviewState) -> Literal["positive_response", "run_diagnosis"]:
        if state['sentiment'] == 'positive':
            return 'positive_response'
        else:
            return 'run_diagnosis'
        
    def positive_response(state: ReviewState):
        prompt = f"""Write a warm thank-you message in response to this review:
        \n\n\"{state['review']}\"\n
    Also, kindly ask the user to leave feedback on our website."""
        
        response = model.invoke(prompt).content
        return {'response': response}
    
    def run_diagnosis(state: ReviewState):
        prompt = f"""Diagnose this negative review:\n\n{state['review']}\n"
        "Return issue_type, tone, and urgency.
    """
        response = structured_model2.invoke(prompt)
        return {'diagnosis': response.model_dump()}
    
    def negative_response(state: ReviewState):
        diagnosis = state['diagnosis']
        
        prompt = f"""You are an empathetic customer support assistant responding to a user who reported an issue.

User's Review: "{state['review']}"

Issue Details:
- Type: {diagnosis['issue_type']}
- User's Tone: {diagnosis['tone']}
- Urgency: {diagnosis['urgency']}

Write a helpful, empathetic response that:
1. Acknowledges their frustration and apologizes for the inconvenience
2. Shows you understand the specific problem they're facing
3. Explains what steps you'll take to help resolve it
4. Provides a realistic timeline or next steps
5. Reassures them that their issue is being taken seriously

DO NOT say the issue is already resolved. The user is currently experiencing the problem.
Be warm, professional, and action-oriented."""
        
        response = model.invoke(prompt).content
        return {'response': response}
    
    # Build workflow
    graph = StateGraph(ReviewState)
    
    graph.add_node('find_sentiment', find_sentiment)
    graph.add_node('positive_response', positive_response)
    graph.add_node('run_diagnosis', run_diagnosis)
    graph.add_node('negative_response', negative_response)
    
    graph.add_edge(START, 'find_sentiment')
    graph.add_conditional_edges('find_sentiment', check_sentiment)
    graph.add_edge('positive_response', END)
    graph.add_edge('run_diagnosis', 'negative_response')
    graph.add_edge('negative_response', END)
    
    st.session_state.workflow = graph.compile()

# App UI
st.title("⭐ AI Review Analyzer")
st.markdown("### Analyze customer reviews and generate intelligent responses")

# Check if workflow view is requested
if st.session_state.get('show_workflow', False):
    st.markdown("---")
    st.markdown("## 🔄 Workflow Visualization")
    st.markdown("This diagram shows how your review flows through the AI system:")
    
    try:
        from IPython.display import Image
        workflow_img = st.session_state.workflow.get_graph().draw_mermaid_png()
        st.image(workflow_img, caption="Review Analysis Workflow", use_container_width=True)
    except:
        st.markdown("```mermaid\n" + st.session_state.workflow.get_graph().draw_mermaid() + "\n```")
    
    st.info("""
    **How it works:**
    1. 🎯 **Sentiment Analysis** - Determines if the review is positive or negative
    2. 🔀 **Conditional Routing** - Routes based on sentiment
    3. 😊 **Positive Path** - Generates a warm thank-you message
    4. 😟 **Negative Path** - Diagnoses the issue (type, tone, urgency) → Creates empathetic support response
    """)
    
    if st.button("⬅️ Back to Analyzer", type="primary", use_container_width=True):
        st.session_state.show_workflow = False
        st.rerun()
    
    st.stop()  # Stop rendering the rest of the page

# Sidebar with info
with st.sidebar:
    st.header("About")
    st.markdown("""
    This app uses AI to:
    - 🎯 Detect sentiment (positive/negative)
    - 🔍 Diagnose issues in negative reviews
    - 💬 Generate personalized responses
    
    **Powered by:**
    - Groq (Free AI API)
    - LangGraph (Workflow)
    - Streamlit (UI)
    """)
    
    st.divider()
    
    st.header("🔄 Workflow")
    if st.button("View Workflow Graph", use_container_width=True):
        st.session_state.show_workflow = True
        st.rerun()
    
    st.divider()
    
    st.header("Examples")
    if st.button("📝 Positive: Product Love", use_container_width=True):
        st.session_state.example_review = "I've been using this product for 3 months now and I'm absolutely blown away! The user interface is incredibly intuitive - I didn't even need to look at the documentation to get started. The performance is lightning-fast, and it's saved me hours of work every week. The customer support team has been amazing too, responding to my questions within minutes. This is hands down the best investment I've made for my business this year. Highly recommend to anyone looking for a reliable solution!"
    
    if st.button("🐛 Critical: Login Bug", use_container_width=True):
        st.session_state.example_review = "I've been trying to log in for over an hour now, and the app keeps freezing on the authentication screen. I've tried everything - clearing cache, reinstalling the app, even switching browsers. Nothing works. This is completely unacceptable, especially since I need to access my work urgently. I have a deadline in 2 hours and I can't get to my files. The app was working fine yesterday, but after today's update, it's completely broken. This kind of bug affecting basic functionality is really disappointing from a paid service."
    
    if st.button("😞 Frustrated: UX Issues", use_container_width=True):
        st.session_state.example_review = "The interface is extremely confusing and poorly designed. I spent 20 minutes just trying to find the export button, which should be front and center. The navigation menu is buried under three different layers, and half the features don't have clear labels. I'm a tech-savvy person, but this app makes me feel like a complete beginner. The lack of tooltips or help guides makes it even worse. For the premium price I'm paying, I expected a much more polished and user-friendly experience."
    
    if st.button("⚡ Performance Complaint", use_container_width=True):
        st.session_state.example_review = "The app is painfully slow. Every action takes 5-10 seconds to load, even simple tasks like opening a document or saving changes. I've checked my internet connection and it's fine - other apps work perfectly. The constant lag is making it impossible to work efficiently. I'm on a decent computer with good specs, so this shouldn't be happening. The performance issues have gotten worse over the past few updates. Really hoping this gets fixed soon because it's affecting my productivity."
    
    if st.button("🤝 Support Request", use_container_width=True):
        st.session_state.example_review = "I've been trying to get help with my account for the past week but haven't received any response from the support team. I sent multiple emails and even tried the live chat, but no one has gotten back to me. My subscription payment failed and now I can't access my account, even though I've already updated my payment method. This lack of communication is really frustrating. I just need someone to manually verify my payment so I can get back to work."

# Main input area
review_text = st.text_area(
    "Enter a customer review:",
    value=st.session_state.get('example_review', ''),
    height=150,
    placeholder="Type or paste a customer review here..."
)

# Analyze button
if st.button("🔍 Analyze Review", type="primary", use_container_width=True):
    if review_text.strip():
        with st.spinner("🤖 Analyzing review..."):
            try:
                # Run workflow
                result = st.session_state.workflow.invoke({
                    'review': review_text
                })
                
                # Display results
                st.success("✅ Analysis Complete!")
                
                # Sentiment badge
                sentiment = result['sentiment']
                if sentiment == 'positive':
                    st.markdown("### 😊 Sentiment: **Positive**")
                else:
                    st.markdown("### 😟 Sentiment: **Negative**")
                
                # If negative, show diagnosis
                if sentiment == 'negative' and result.get('diagnosis'):
                    st.markdown("---")
                    st.markdown("### 🔍 Issue Diagnosis")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        issue_type = result['diagnosis']['issue_type']
                        st.metric("Issue Type", issue_type)
                    with col2:
                        tone = result['diagnosis']['tone']
                        st.metric("Tone", tone.capitalize())
                    with col3:
                        urgency = result['diagnosis']['urgency']
                        urgency_color = {"low": "🟢", "medium": "🟡", "high": "🔴"}
                        st.metric("Urgency", f"{urgency_color.get(urgency, '')} {urgency.capitalize()}")
                
                # Generated response
                st.markdown("---")
                st.markdown("### 💬 AI-Generated Response")
                
                # Display the response in a text area for easy copying
                st.text_area(
                    "Response:",
                    value=result['response'],
                    height=400,
                    label_visibility="collapsed"
                )
                
                # Add copy button
                if st.button("📋 Copy to Clipboard", use_container_width=True):
                    st.toast("✅ Response copied to clipboard!", icon="✅")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Make sure you've set up your GROQ_API_KEY in the .env file")
    else:
        st.warning("⚠️ Please enter a review to analyze")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        Built with ❤️ using Streamlit & LangGraph<br>
        <a href='https://amaanshaikh.netlify.app/' target='_blank' style='color: #4A90E2; text-decoration: none;'>
            👨‍💻 View My Portfolio
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
