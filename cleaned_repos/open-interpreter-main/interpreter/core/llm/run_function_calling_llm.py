from .utils.merge_deltas import merge_deltas
from .utils.parse_partial_json import parse_partial_json

function_schema = {
    "name": "execute",
    "description": "Executes code on the user's machine **in the users local environment** and returns the output",
    "parameters": {
        "type": "object",
        "properties": {
            "language": {
                "type": "string",
                "description": "The programming language (required parameter to the `execute` function)",
                "enum": [],
            },
            "code": {"type": "string", "description": "The code to execute (required)"},
        },
        "required": ["language", "code"],
    },
}


def run_function_calling_llm(llm, request_params):
    ## Setup

    # Add languages OI has access to
    function_schema["parameters"]["properties"]["language"]["enum"] = [
        i.name.lower() for i in llm.interpreter.computer.terminal.languages
    ]
    request_params["functions"] = [function_schema]

    # Add OpenAI's recommended function message
    request_params["messages"][0][
        "content"
    ] += "\nUse ONLY the function you have been provided with — 'execute(language, code)'."

    ## Convert output to LMC format

    accumulated_deltas = {}
    language = None
    code = ""

    for chunk in llm.completions(**request_params):
        if "choices" not in chunk or len(chunk["choices"]) == 0:
            # This happens sometimes
            continue

        delta = chunk["choices"][0]["delta"]

        # Accumulate deltas
        accumulated_deltas = merge_deltas(accumulated_deltas, delta)

        if "content" in delta and delta["content"]:
            yield {"type": "message", "content": delta["content"]}

        if (
            accumulated_deltas.get("function_call")
            and "arguments" in accumulated_deltas["function_call"]
        ):
            if (
                "name" in accumulated_deltas["function_call"]
                and accumulated_deltas["function_call"]["name"] == "execute"
            ):
                arguments = accumulated_deltas["function_call"]["arguments"]
                arguments = parse_partial_json(arguments)

                if arguments:
                    if (
                        language is None
                        and "language" in arguments
                        and "code"
                        in arguments  # <- This ensures we're *finished* typing language, as opposed to partially done
                        and arguments["language"]
                    ):
                        language = arguments["language"]

                    if language is not None and "code" in arguments:
                        # Calculate the delta (new characters only)
                        code_delta = arguments["code"][len(code) :]
                        # Update the code
                        code = arguments["code"]
                        # Yield the delta
                        if code_delta:
                            yield {
                                "type": "code",
                                "format": language,
                                "content": code_delta,
                            }
                else:
                    if llm.interpreter.verbose:
                        print("Arguments not a dict.")

            # Common hallucinations
            elif "name" in accumulated_deltas["function_call"] and (
                accumulated_deltas["function_call"]["name"] == "python"
                or accumulated_deltas["function_call"]["name"] == "functions"
            ):
                if llm.interpreter.verbose:
                    print("Got direct python call")
                if language is None:
                    language = "python"

                if language is not None:
                    # Pull the code string straight out of the "arguments" string
                    code_delta = accumulated_deltas["function_call"]["arguments"][
                        len(code) :
                    ]
                    # Update the code
                    code = accumulated_deltas["function_call"]["arguments"]
                    # Yield the delta
                    if code_delta:
                        yield {
                            "type": "code",
                            "format": language,
                            "content": code_delta,
                        }

            else:
                # If name exists and it's not "execute" or "python" or "functions", who knows what's going on.
                if "name" in accumulated_deltas["function_call"]:
                    print(
                        "Encountered an unexpected function call: ",
                        accumulated_deltas["function_call"],
                        "\nPlease open an issue and provide the above info at: https://github.com/KillianLucas/open-interpreter",
                    )
