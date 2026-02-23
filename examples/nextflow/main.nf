#!/usr/bin/env nextflow

nextflow.enable.dsl=2

params.input   = null
params.config  = null
params.outdir  = "results"
params.threads = 1

process CODON_OPTIMIZE {
    publishDir "${params.outdir}", mode: 'copy'

    input:
    path fasta
    path config

    output:
    path "optimized.fna", emit: fasta
    path "summary.tsv",   emit: tsv

    script:
    """
    cc_copt optimize \
        -i ${fasta} \
        -c ${config} \
        -o optimized.fna \
        -t summary.tsv \
        --threads ${params.threads}
    """
}

workflow {
    if (!params.input || !params.config) {
        error "Usage: nextflow run main.nf --input INPUT.faa --config CONFIG.yaml [--outdir results] [--threads 1]"
    }

    input_ch  = Channel.fromPath(params.input)
    config_ch = Channel.fromPath(params.config)

    CODON_OPTIMIZE(input_ch, config_ch)
}
