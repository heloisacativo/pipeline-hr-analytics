terraform {
    required_providers {
        oci = {
            source = "oracle/oci"
            version = ">=7.0.0"
        }
        local = { source = "hashicorp/local", version = ">= 2.0.0" }
        null  = { source = "hashicorp/null",  version = ">= 3.0.0" }
    }
}

provider "oci" {
  config_file_profile = "DEFAULT"
  region = "sa-saopaulo-1" 
}

