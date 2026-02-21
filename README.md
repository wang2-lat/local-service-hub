# Local Service Hub

CLI tool for local service providers to manage leads and contractor network.

## Features

- **Service Provider Management**: Add and track service providers with their specialties and coverage areas
- **Smart Lead Matching**: Automatically match customer leads with qualified providers based on service type and location
- **Contractor Network**: Maintain a database of reliable contractors with reliability ratings
- **Lead Tracking**: Manage customer leads from creation to completion

## Installation


## Usage

### Add a Service Provider


### List All Providers


Filter by service type:

### Rate a Provider


### Add a Customer Lead


The system will automatically match the lead with available providers.

### List Leads


Filter by status:

### Match a Lead Manually


### Close a Lead


### View Statistics


## Example Workflow

1. Add service providers to your network:
   ```bash
   python main.py provider-add
   ```

2. When a customer inquiry comes in, add it as a lead:
   ```bash
   python main.py lead-add
   ```

3. The system automatically finds matching providers based on service type and location

4. Rate providers after job completion:
   ```bash
   python main.py provider-rate 1 9
   ```

5. Close completed leads:
   ```bash
   python main.py lead-close 1
   ```

## Database

Data is stored in `service_hub.db` (SQLite) in the current directory.