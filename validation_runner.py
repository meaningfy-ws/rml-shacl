import os
import logging
import argparse
from rdflib import Graph
from src.mapping_validator import MappingValidator

def configure_logging(output_method, report_file=None):
    if output_method == 'console':
        logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')
    elif output_method == 'file' and report_file:
        logging.basicConfig(filename=report_file, filemode='w', level=logging.INFO, format='%(levelname)s:%(message)s')
    else:
        raise ValueError("Invalid output method or missing report file for file output.")

def validate_rml_files(paths, shape_file, output_method, report_file=None, combined=False):
    configure_logging(output_method, report_file)
    validator = MappingValidator(shape_file)
    
    if combined:
        combined_graph = Graph()
        for path in paths:
            if os.path.isfile(path):
                load_graph(path, combined_graph)
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.endswith('.ttl'):  # Assuming RML files are in Turtle format
                            load_graph(os.path.join(root, file), combined_graph)
        validate_combined_graph(combined_graph, validator)
    else:
        for path in paths:
            if os.path.isfile(path):
                validate_file(path, validator)
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.endswith('.ttl'):  # Assuming RML files are in Turtle format
                            validate_file(os.path.join(root, file), validator)

def load_graph(file_path, graph):
    try:
        graph.parse(file_path, format='turtle')
        logging.info(f"Loaded {file_path} into combined graph")
        print(f"Loaded {file_path} into combined graph")
    except Exception as e:
        print(f"Failed to load {file_path}: {e}")
        logging.error(f"Failed to load {file_path}: {e}")

def validate_combined_graph(graph, validator):
    try:
        validator.validate(graph)
        logging.info("Combined validation successful")
    except Exception as e:
        logging.error(f"Combined validation failed: {e}")

def validate_file(file_path, validator):
    try:
        g = Graph()
        g.parse(file_path, format='turtle')
        validator.validate(g)
        logging.info(f"Validation successful for {file_path}")        
        print(f"Validation successful for {file_path}")
    except Exception as e:
        logging.info(f"Validation failed for {file_path}: {e}")
        print(f"Validation failed for {file_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RML files against SHACL shapes.")
    parser.add_argument('rml_paths', nargs='+', help="RML file or directory paths to validate.")
    parser.add_argument('--shape-file', default=os.path.abspath('rml_rules_shape.ttl'), help="Path to the SHACL shape file.")
    parser.add_argument('--output', choices=['console', 'file'], default='file', help="Output method for the validation report.")
    parser.add_argument('--report-file', default='validation_report.txt', help="File to write the validation report if output method is 'file'.")
    parser.add_argument('--combined', action='store_true', help="Combine all files into a single graph for validation.")

    args = parser.parse_args()

    validate_rml_files(args.rml_paths, args.shape_file, args.output, args.report_file, args.combined)
