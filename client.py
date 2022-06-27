#!/usr/bin/env python3

import sys
import argparse
import os.path
from pathlib import Path
import requests
import json
import platform
import time
import traceback

BACKENDS = ["silicon", "carbon"]
COMMAND = ["verify", "terminate"]
PRINTMODE = ["format", "bulk"]


def create_argument_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-j", "--format",
        help="Choose between nicely-[format]ted Json output vs [bulk]-friendly.",
        choices=PRINTMODE,
        default="format")

    parser.add_argument(
        "-c", "--command",
        help="Specify the command for the server.",
        choices=COMMAND,
        default="verify")

    parser.add_argument(
        "-p", "--port",
        help="Specify the port listened by ViperServer.",
        type=int,
        required=True)

    parser.add_argument(
        "-f", "--file",
        help="File to verify. Must be a Viper program.",
        default="__empty_viper_file__.vpr")

    parser.add_argument(
        "-v", "--verifier",
        help="Specify which verification backend to use.",
        #choices=backends, -- we might need to use custom backends
        default="silicon"
        )

    parser.add_argument(
        "-x", "--options",
        default=( "--disableCaching  --z3Exe=/usr/local/Viper/z3/bin/z3" if not platform.system()=="Windows" else
                  "--disableCaching '--z3Exe=C:\\Program Files\\Viper\\z3\\bin\\z3.exe'"),
        help="Pass an options string to the verifier.")

    parser.add_argument(
        "--additional-options",
        help="Pass additional options string to the verifier.")

    parser.add_argument(
        "--benchmark-report-dir",
        help="Where to put the benchmark report",
        default=".",
    )

    parser.add_argument(
        "--warmup-file",
        help="The file to use for warming up JVM",
    )

    parser.add_argument(
        "--warmup-reps",
        type=int,
        default=6,
        help="How many iterations to use for warming up JVM",
    )

    parser.add_argument(
        "--benchmark",
        help="Benchmark the specified files",
        nargs='+',
    )

    parser.add_argument(
        "--benchmark-reps",
        type=int,
        default=10,
        help="How many iterations to use for benchmarking",
    )

    return parser


def benchmark_verify(log_file, port, verifier, options, file):
    if not Path(file).is_file():
        print(f"File `{file}` does not exist.")
        sys.exit(1)
    verification_backend = verifier
    id = initiate_verification(port, verification_backend, options, file)
    verification_results = requests.get(
        f"http://localhost:{port}/verify/{id}",
    )
    log_file.write('\n\nBENCHMARK_VERIFY:\n')
    log_file.write(f'{verifier} {options} {file}\n')
    log_file.write(verification_results.text)
    log_file.flush()
    time = None
    for line in verification_results.iter_lines():
        message = json.loads(line.decode())
        if message['msg_type'] == 'verification_result':
            assert message['msg_body']['status'] == 'success', message
            assert message['msg_body']['verifier'] == verifier, message
            if message['msg_body']['kind'] == 'for_entity':
                assert not message['msg_body']['details']['cached'], message
            elif message['msg_body']['kind'] == 'overall':
                assert time is None
                time = message['msg_body']['details']['time']
            else:
                assert False, f"unexpected kind: {message['msg_body']['kind']}"
    assert time is not None
    return time


def benchmark(
        port, verifier, options, warmup_file, warmup_reps, files,
        benchmark_reps, benchmark_report_dir
    ):
    assert len(files) == len(set(files)), 'file names are not unique'
    report = {}
    timestamp = time.time()
    os.makedirs(benchmark_report_dir, exist_ok=True)
    benchmark_report = os.path.join(benchmark_report_dir, f'report-{str(timestamp)}.json')
    with open(benchmark_report, 'w') as report_file:
        try:
            with open('benchmark.log', 'w') as log_file:
                while warmup_reps > 0:
                    duration = benchmark_verify(log_file, port, verifier, options, warmup_file)
                    warmup_reps -= 1
                    print(f'warm-up iteration {warmup_reps} time: {duration}ms')
                for file in files:
                    print(f'benchmarking: {file}')
                    durations = []
                    reps = benchmark_reps
                    while reps > 0:
                        duration = benchmark_verify(log_file, port, verifier, options, file)
                        reps -= 1
                        print(f'  iteration {reps} time: {duration}ms')
                        durations.append(duration)
                    report[file] = durations
        finally:
            report_file.write(json.dumps(report, indent = 2))


def terminate(port):
    r = requests.get("http://localhost:" + str(port) + "/exit")
    print(r.text)
    sys.exit(0)


def verify(port, verifier, options, file, format):
    if not Path(file).is_file():
        print(f"File `{file}` does not exist.")
        sys.exit(1)
    verification_backend = verifier
    id = initiate_verification(port, verification_backend, options, file)
    print(f'verification id: {id}')
    # #print("[AST] Requesting to stream AST construction results:")
    # #AST = requests.get("http://localhost:" + str(args.port) + "/ast/" +
    # #                   str(ast_id),
    # #                   stream=True)
    # #print(AST)
    # #print(AST.text)
    # #print_formatted_response(AST)
    # time.sleep(10)
    print("[VER] Requesting to stream verification results:")
    verification_results = requests.get(
        f"http://localhost:{port}/verify/{id}",
        stream=True
    )
    print_formatted_response(verification_results, format)


def print_formatted_response(response, format):
    if format == "format":
        for line in response.iter_lines():
            if line:
                jsonString = line.decode("utf-8")
                try:
                    json_data = json.loads(jsonString)
                except Exception as e:
                    print('decoding line "' + jsonString + '" has failed')
                    traceback.print_exc()
                else:
                    print(json.dumps(json_data, indent=2))
                    if "--writeLogFile" in args.options:
                        if json_data["msg_type"] == "symbolic_execution_logger_report":
                            with open("genericNodes.json", 'w') as f:
                                f.write(json.dumps(json_data["msg_body"], indent=2))
    else:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk: # filter out keep-alive new chunks
                print(chunk.decode("utf-8"), end='')
        print('\n')


def initiate_verification(port, verification_backend, options, file):
    headers = {'Content-Type': 'application/json'}
    req = {
        'arg': f'{verification_backend} {options} "{os.path.abspath(file)}"'
    }
    response = requests.post(
        f"http://localhost:{port}/verify",
        data=json.dumps(req),
        headers=headers,
        timeout=5
    )
    return response.json()['id']


def compute_options(parser, args):
    if parser.get_default("options") == args.options:
        if args.verifier != "carbon":
            print(f"[viper_client] Default backend options set to: \n"
                  f"  {args.options}\n   (Override with -x)")
        else:
            default_carbon_options=( "  --boogieExe=/usr/local/Viper/boogie/Binaries/Boogie" if platform.system()=="Darwin" else
                                     " '--boogieExe=C:\\Program Files\\Viper\\boogie\\Binaries\\Boogie.exe'")
            print("[viper_client] Default backend options (for carbon) set to: \n" +
                  "[viper_client]   " + args.options + default_carbon_options + "\n" +
                  "[viper_client]   (Override with -x)")
            args.options += default_carbon_options
    options = args.options
    if args.additional_options is not None:
        options += ' ' + args.additional_options
    return options


def main():
    parser = create_argument_parser()
    args = parser.parse_args()
    if args.benchmark:
        files = args.benchmark
        options = compute_options(parser, args)
        assert args.warmup_file is not None, 'Please specify the warm-up file.'
        benchmark(
            args.port, args.verifier, options,
            args.warmup_file, args.warmup_reps,
            args.benchmark, args.benchmark_reps,
            args.benchmark_report_dir
        )
    elif args.command == "terminate":
        terminate(args.port)
    else:
        assert args.command == 'verify'
        if parser.get_default("file") == args.file:
            print("[viper_client] Testing ViperClient with an empty Viper file. Reason: no file is specified via option -f.")
        options = compute_options(parser, args)
        verify(args.port, args.verifier, options, args.file, format)


if __name__ == '__main__':
    main()

