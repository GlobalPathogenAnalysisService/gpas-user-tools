#!/usr/bin/env python3

import math
import pathlib
import argparse

from typing import List


def chunks(lst, n):
    """
    Yield successive n-sized chunks from provided list.
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def build_csv(
    filename: str,
    guids: List[str],
    fastq1s: List,
    fastq2s: List,
    collection_date: str,
    country: str,
    pipeline: str,
    tech: str,
):
    """
    Build a CSV file for upload to the Genomic Pathogen Analysis System (GPAS).
    """
    with open(filename, "w") as out:
        out.write(
            "batch_name,sample_name,reads_1,reads_2,control,collection_date,country,subdivision,district,specimen_organism,host_organism,instrument_platform\n"
        )
        for sample, f1, f2 in zip(guids, fastq1s, fastq2s):
            out.write(
                f",{sample},{f1},{f2},,{collection_date},{country},,,{pipeline},homo sapiens,{tech}\n"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-dir",
        default=".",
        help="the path to the folder containing the FASTQ files",
    )
    parser.add_argument(
        "--fastq1-suffix",
        default="_1.fastq.gz",
        help="how all the first FASTQ filenames end",
    )
    parser.add_argument(
        "--fastq2-suffix",
        default="_2.fastq.gz",
        help="how all the second FASTQ filenames end",
    )
    parser.add_argument(
        "--collection-date",
        default="2024-01-01",
        help="the date the sample was collected in ISO format e.g. 2024-02-29",
    )
    parser.add_argument(
        "--country",
        default="GBR",
        help="the name of the country where the samples were collected",
    )
    parser.add_argument(
        "--tech",
        default="illumina",
        help="whether to generate illumina (paired) or nanopore (unpaired) reads",
    )
    parser.add_argument(
        "--pipeline",
        default="mycobacteria",
        help="target pipeline; currently only mycobacteria is supported",
    )
    parser.add_argument(
        "--output",
        default="upload.csv",
        help="the name of the CSV file to be generated",
    )
    parser.add_argument(
        "--number-of-batches",
        default=1,
        type=int,
        help="how many batches to generate",
    )
    parser.add_argument(
        "--max-samples-in-batch",
        default=100,
        type=int,
        help="the maximum number of samples in a single batch",
    )

    options = parser.parse_args()

    assert (
        options.pipeline == "mycobacteria"
    ), "Currently only mycobacteria is supported"
    assert options.max_samples_in_batch > 0, "Max samples in batch must be > 0"
    assert options.number_of_batches > 0, "Number of batches must be > 0"
    assert options.tech == "illumina", "Currently only illumina is supported"
    assert (
        len(options.country) == 3
    ), "Country code must conform to ISO 3166 i.e. be 3 characters long"

    path = pathlib.Path(options.input_dir)
    assert path.is_dir(), "Input directory does not exist"

    if options.tech == "illumina":
        fastqs1 = [f for f in path.glob(f"*{options.fastq1_suffix}")]
        fastqs2 = [f for f in path.glob(f"*{options.fastq2_suffix}")]

        # sort the lists alphabetically to ensure the files are paired correctly
        fastqs1.sort()
        fastqs2.sort()

        assert (
            options.fastq1_suffix != options.fastq2_suffix
        ), "FASTQ suffixes must be different"

        assert len(fastqs1) == len(
            fastqs2
        ), "Each sample must have two FASTQ files -> check the suffices of the FASTQ files and that they match what is specified in the command-line options"

        guids = [f.name.replace(options.fastq1_suffix, "") for f in fastqs1]

    n_samples_per_batch = math.ceil(len(guids) / options.number_of_batches)
    n_batches = options.number_of_batches
    if n_samples_per_batch > options.max_samples_in_batch:
        n_samples_per_batch = options.max_samples_in_batch
        n_batches = math.ceil(len(guids) / n_samples_per_batch)

    batch_files = []
    if n_batches == 1:
        batch_files.append(options.output)
        build_csv(
            options.output,
            guids,
            fastqs1,
            fastqs2,
            options.collection_date,
            options.country,
            options.pipeline,
            options.tech,
        )
    else:
        for i, batch in enumerate(chunks(guids, n_samples_per_batch)):
            outfile = f"{options.output.replace('.csv', '')}_{i}.csv"
            batch_files.append(outfile)
            build_csv(
                outfile,
                batch,
                fastqs1,
                fastqs2,
                options.collection_date,
                options.country,
                options.pipeline,
                options.tech,
            )

    print(f"Generated {n_batches} CSV files: {', '.join(batch_files)}\n")
    print(
        "To upload with the GPAS CLI, issue the following commands after your terminal command prompt (here $):"
    )
    print()
    print("$ gpas auth")
    print()
    print("and enter your username (usually your email address) and password\n")
    print(
        "Then type the following; note that each batch takes a while to complete, depending on how many samples it contains, the number of CPU cores on your machine and the speed of your internet connection.\n"
    )
    for i in batch_files:
        print(f"$ gpas upload {i}\n")
