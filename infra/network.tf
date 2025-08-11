
data "oci_core_services" "all_services" {}

output "all_service_names" {
  value = [for s in data.oci_core_services.all_services.services : s.name]
}

output "object_storage_service" {
  value = local.object_storage_service
}

locals {
  object_storage_service = one([
    for s in data.oci_core_services.all_services.services : s
    if s.name == "OCI GRU Object Storage"
  ])
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}

resource "oci_core_virtual_network" "vcn_airflow" {
  compartment_id = var.compartment_id
  display_name   = "vcn-airflow"
  cidr_block     = "10.0.0.0/16"
}

resource "oci_core_internet_gateway" "ig" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_virtual_network.vcn_airflow.id
  display_name   = "internet-gateway-airflow"
}

resource "oci_core_service_gateway" "service_gateway" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_virtual_network.vcn_airflow.id

  services {
    service_id = data.oci_core_services.all_services.services[0].id
  }
}

resource "oci_core_route_table" "rt" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_virtual_network.vcn_airflow.id
  display_name   = "airflow-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.ig.id
  }

  route_rules {
    destination       = local.object_storage_service.cidr_block
    destination_type  = "SERVICE_CIDR_BLOCK"
    network_entity_id = oci_core_service_gateway.service_gateway.id
  }
}

resource "oci_core_subnet" "subnet_airflow" {
  compartment_id     = var.compartment_id
  vcn_id             = oci_core_virtual_network.vcn_airflow.id
  cidr_block         = "10.0.1.0/24"
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  route_table_id     = oci_core_route_table.rt.id
}


