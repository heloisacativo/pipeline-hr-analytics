resource "oci_database_autonomous_database" "adb" {
  compartment_id               = var.compartment_id
  display_name                 = var.db_display_name
  db_name                      = var.db_name
  cpu_core_count               = var.cpu_core_count
  data_storage_size_in_tbs     = var.data_storage_size_in_tbs
  is_free_tier                 = true

  admin_password               = var.adb_admin_password
  whitelisted_ips              = var.whitelisted_ips

  lifecycle {
    ignore_changes = [
      cpu_core_count,
      data_storage_size_in_tbs,
      is_auto_scaling_enabled, 
      subnet_id,               
      private_endpoint_label,
      nsg_ids,
    ]
  }
}

resource "oci_database_autonomous_database_wallet" "wallet" {
  autonomous_database_id = oci_database_autonomous_database.adb.id
  password               = var.adb_wallet_password

  base64_encode_content  = true
  generate_type          = "SINGLE"
}

resource "local_file" "adb_wallet_zip" {
  filename       = "${path.module}/wallet/adb_wallet.zip"
  content_base64 = oci_database_autonomous_database_wallet.wallet.content
}

resource "null_resource" "unzip_wallet" {
  depends_on = [local_file.adb_wallet_zip]

  provisioner "local-exec" {
    interpreter = ["C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass"]
    command = <<EOT
      $out = "${path.module}/wallet/adb_wallet"
      if (-not (Test-Path $out)) {
        New-Item -ItemType Directory -Path $out | Out-Null
      }
      Expand-Archive -Path "${path.module}/wallet/adb_wallet.zip" -DestinationPath $out -Force
    EOT
  }
}


output "adb_state" {
  value = oci_database_autonomous_database.adb.state
}

output "connect_string_high" {
  value = oci_database_autonomous_database.adb.connection_strings[0].high
}

output "connect_string_medium" {
  value = oci_database_autonomous_database.adb.connection_strings[0].medium
}

output "connect_string_low" {
  value = oci_database_autonomous_database.adb.connection_strings[0].low
}

output "wallet_zip_path" {
  value = local_file.adb_wallet_zip.filename
}

output "wallet_folder" {
  value = "${path.module}/wallet/adb_wallet"
  depends_on = [null_resource.unzip_wallet]
}