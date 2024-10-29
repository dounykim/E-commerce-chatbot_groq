import opik

opik_client = opik.Opik(project_name='Trendy Fashion', workspace='dounykim')

def opik_trace(input_data, output, context):
    trace = opik_client.trace(
        name='chat',
        input={'user_input': input_data},
        output={'response': output}
    )

    trace.span(
        name='llm_call',
        type='llm',
        input={'context': context},
        output={'response': output}
    )
