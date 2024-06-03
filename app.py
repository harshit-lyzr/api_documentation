import streamlit as st
from lyzr_automata.ai_models.openai import OpenAIModel
from lyzr_automata import Agent, Task
from lyzr_automata.pipelines.linear_sync_pipeline import LinearSyncPipeline
from PIL import Image
from lyzr_automata.tasks.task_literals import InputType, OutputType

st.set_page_config(
    page_title="API Documentation Generator📑",
    layout="centered",  # or "wide"
    initial_sidebar_state="auto",
    page_icon="lyzr-logo-cut.png",
)

api = st.sidebar.text_input("Enter Your OPENAI API KEY HERE", type="password")

st.markdown(
    """
    <style>
    .app-header { visibility: hidden; }
    .css-18e3th9 { padding-top: 0; padding-bottom: 0; }
    .css-1d391kg { padding-top: 1rem; padding-right: 1rem; padding-bottom: 1rem; padding-left: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

image = Image.open("lyzr-logo.png")
st.image(image, width=150)

# App title and introduction
st.title("API Documentation Generator📑")
st.sidebar.markdown("## Welcome to the API Documentation Generator!")
st.sidebar.markdown(
    "This App Harnesses power of Lyzr Automata to Create API Documentation. You Need to input Your API function with Endpoint and this app create API Documenetation.")
st.sidebar.markdown("""
Example Code:

    @app.route('/sum', methods=['POST'])
    def sum_numbers():
        data = request.get_json()
        num1 = data['num1']
        num2 = data['num2'] 

        try:
            result = num1 + num2
            return jsonify({'result': result}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
""")

if api:
    openai_model = OpenAIModel(
        api_key=api,
        parameters={
            "model": "gpt-4-turbo-preview",
            "temperature": 0.2,
            "max_tokens": 1500,
        },
    )
else:
    st.sidebar.error("Please Enter Your OPENAI API KEY")


def api_documentation(code_snippet):
    documentation_agent = Agent(
        prompt_persona="You Are Expert In API Documentation Creation.",
        role="API Documentation Expert",
    )

    documentation_task = Task(
        name="API Documentation converter",
        output_type=OutputType.TEXT,
        input_type=InputType.TEXT,
        model=openai_model,
        agent=documentation_agent,
        log_output=True,
        instructions=f"""You Are Expert In API Documentation Creation.
        Your Task Is to Create API Documentation For given API Endpoint and code.
        Follow Below Format and Instruction:
        DO NOT WRITE INTRODUCTION AND CONCLUSION.
        Endpoint: Specify the HTTP method (GET, POST, PUT, DELETE) and the full path of the endpoint (e.g., /api/v1/users).
        Request Headers: List required and optional headers, including content type and authorization.
        Path Parameters: Describe any parameters that are part of the URL path (e.g., /api/v1/users/user_id).Include the parameter name, data type, and a brief description.
        Query Parameters: List any query parameters accepted by the endpoint.Include the parameter name, data type, required/optional status, and a brief description.Provide example query strings.
        Request Body: For endpoints that accept a body (e.g., POST, PUT), describe the body format (JSON, XML).Provide a schema or example of the request body, including data types and required/optional fields.
        Response Format: Describe the response format (usually JSON).Provide a schema or example of the response body, including data types.
        Response Codes: List possible HTTP status codes returned by the endpoint.Provide a brief description for each status code, explaining what it means (e.g., 200 OK, 404 Not Found).
        Examples: Include example requests and responses for common use cases.Provide code snippets in various programming languages if possible.

        Code: {code_snippet}
        """,
    )

    output = LinearSyncPipeline(
        name="Generate Documentation",
        completion_message="Documentation Generated!",
        tasks=[
            documentation_task
        ],
    ).run()
    return output[0]['task_output']


code = st.text_area("Enter Code", height=300)

if st.button("Generate"):
    solution = api_documentation(code)
    st.markdown(solution)
