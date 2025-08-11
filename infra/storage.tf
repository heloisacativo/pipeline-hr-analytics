data "oci_objectstorage_namespace" "ns" {}

resource "oci_objectstorage_bucket" "bucket-hr-analytics" {
  compartment_id = var.compartment_id
  name           = "bucket-hr-analytics"
  namespace      = data.oci_objectstorage_namespace.ns.namespace
}
