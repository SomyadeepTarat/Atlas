from opentelemetry import metrics

meter = metrics.get_meter(
    "atlas",
    "0.1.0",
)

model_calls = meter.create_counter(
    name="atlas.model.calls",
    unit="1",
)

model_input_tokens = meter.create_counter(
    name="atlas.model.input_tokens",
    unit="token",
)

model_output_tokens = meter.create_counter(
    name="atlas.model.output_tokens",
    unit="token",
)

research_requests = meter.create_counter(
    name="atlas.research.requests",
    unit="1",
    description=("Number of research requests."),
)

research_duration = meter.create_histogram(
    name="atlas.research.duration",
    unit="s",
    description=("Research workflow duration."),
)

retrieval_duration = meter.create_histogram(
    name="atlas.retrieval.duration",
    unit="s",
)
