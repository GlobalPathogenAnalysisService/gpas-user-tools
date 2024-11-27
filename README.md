> [!CAUTION]  
> # Archived for historical purposes
> This functionality has been merged into the [client](https://github.com/EIT-Pathogena/client), and this repository will get no further updates







# gpas-user-tools
Collection of tools to help users upload, process and download FASTQ files for GPAS. This is a quick repository intended to help the users taking part in the GPAS pilot and is not yet production code. At present it is limited to
* Illumina paired FASTQs
* Mycobacterial samples

For example, consider having a folder `data/` containing 10 pairs of illumina FASTQ files named `sample01_1.fastq.gz`, `sample01_2.fastq.gz`... `sample10_1.fastq.gz`, `sample10_2.fastq.gz`.

If I want to composite a basic upload CSV file where the samples where all collected in England on 10 Jan 2024 I would issue

```
$ python gpas-create-uploadcsv.py --input-dir data/ --collection-date 2024-01-10 --country GBR
```

Note that the date has to be in ISO-8601 format and the country has to be a valid ISO-3166 3-letter code, here `GBR`. This will then produce a single file `upload.csv` specifying all ten samples. One can then edit this file to e.g. modify some of the collection dates or make some of the samples `positive` or `negative` controls.

On the other hand, if I want to upload these ten samples as two batches, I can issue

```
$ python gpas-create-uploadcsv.py --input-dir data/ --collection-date 2024-01-10 --country GBR --number-of-batches 2
```

And two files, `upload-0.csv` and `upload-1.csv`, will be created each with five samples. This can be useful if e.g. your network connection occasionally drops.


