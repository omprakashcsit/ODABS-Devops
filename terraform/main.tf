terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = "45d76ad9-2a44-44fa-8445-03fd64585d01"
}

resource "azurerm_resource_group" "odabs" {
  name     = "odabs-terraform-rg"
  location = "centralindia"
}

resource "azurerm_virtual_network" "odabs" {
  name                = "odabs-vnet"
  location            = azurerm_resource_group.odabs.location
  resource_group_name = azurerm_resource_group.odabs.name
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "odabs" {
  name                 = "odabs-subnet"
  resource_group_name  = azurerm_resource_group.odabs.name
  virtual_network_name = azurerm_virtual_network.odabs.name
  address_prefixes     = ["10.0.1.0/24"]
}


resource "azurerm_network_security_group" "odabs" {
  name                = "odabs-nsg"
  location            = azurerm_resource_group.odabs.location
  resource_group_name = azurerm_resource_group.odabs.name
}

resource "azurerm_network_security_rule" "ssh" {
  name                        = "allow-ssh"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "22"
  source_address_prefix      = "*"
  destination_address_prefix = "*"
  resource_group_name         = azurerm_resource_group.odabs.name
  network_security_group_name = azurerm_network_security_group.odabs.name
}

resource "azurerm_network_security_rule" "http" {
  name                        = "allow-http"
  priority                    = 110
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "80"
  source_address_prefix      = "*"
  destination_address_prefix = "*"
  resource_group_name         = azurerm_resource_group.odabs.name
  network_security_group_name = azurerm_network_security_group.odabs.name
}


resource "azurerm_public_ip" "odabs" {
  name                = "odabs-public-ip"
  location            = azurerm_resource_group.odabs.location
  resource_group_name = azurerm_resource_group.odabs.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_network_interface" "odabs" {
  name                = "odabs-nic"
  location            = azurerm_resource_group.odabs.location
  resource_group_name = azurerm_resource_group.odabs.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.odabs.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.odabs.id
  }
}


resource "azurerm_linux_virtual_machine" "odabs" {
  name                = "odabs-vm"
  resource_group_name = azurerm_resource_group.odabs.name
  location            = azurerm_resource_group.odabs.location
  size                = "Standard_B2s_v2"
  admin_username      = "azureuser"

  network_interface_ids = [
    azurerm_network_interface.odabs.id
  ]

  admin_ssh_key {
    username   = "azureuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }
}
