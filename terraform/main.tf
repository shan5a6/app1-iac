module "vpc" {
  source = "./modules/vpc"
  applicationname = var.applicationname
  environment     = var.environment
  cidr_block      = var.cidr_block
  public_subnet_cidr_block = var.public_subnet_cidr_block
  private_subnet_cidr_block = var.private_subnet_cidr_block
  availability_zone = var.availability_zone
  region            = var.region
}
