# VIKMO Assignment - Design Decisions

## Database Design

### Product
- SKU is unique to ensure each product can be identified and searched efficiently.
- External ID is stored to support channel synchronization.

### Inventory
- Inventory uses a OneToOne relationship with Product because each product must have exactly one inventory record.

### Dealer
- Dealer stores customer information and can place multiple orders.

### Order
- Order stores dealer orders and tracks status transitions:
  - DRAFT
  - CONFIRMED
  - DELIVERED

- Order numbers are auto-generated using the format:
  ORD-YYYYMMDD-XXXX

### OrderItem
- OrderItem links Orders and Products.
- Unit price is stored separately to preserve historical pricing even if the Product price changes later.
- line_total is stored to preserve the value calculated at the time of ordering and avoid recalculation issues if prices change later.

## Relationship Design

### Product → Inventory
- OneToOneField was chosen because each product should have exactly one inventory record.
- This prevents duplicate inventory records for the same product.

### Dealer → Order
- ForeignKey relationship was used because one dealer can place multiple orders.
- on_delete=PROTECT was chosen to prevent deleting a dealer that already has orders.

### Order → OrderItem
- ForeignKey relationship was used because one order can contain multiple items.
- on_delete=CASCADE was chosen because order items should be removed automatically if the parent order is deleted.

### OrderItem → Product
- on_delete=PROTECT was chosen because products referenced by existing orders should not be deleted.
- This preserves historical order information.

## Business Logic

### Stock Validation
- Stock is validated before confirming an order.
- If any product has insufficient stock, the entire confirmation process is rejected.
- The user receives a clear error message showing available and requested quantities.

### Stock Deduction
- Stock is deducted only when an order moves from DRAFT to CONFIRMED.
- Draft orders have no inventory impact.

### Order Status Flow
- DRAFT → editable
- CONFIRMED → locked
- DELIVERED → final state

- Invalid transitions are rejected.
- Confirmed and Delivered orders cannot be modified or deleted.

## Concurrency and Data Integrity

### Transaction Strategy

Order confirmation is wrapped inside a transaction using:

- transaction.atomic()

This ensures that stock deductions are treated as a single unit of work.

If any product fails stock validation, the entire transaction is rolled back and no inventory changes are saved.

### Locking Strategy

During order confirmation, inventory rows are locked using:

- select_for_update()

This prevents two users from confirming orders against the same inventory at the same time.

Example:

- Product stock = 1
- Dealer A attempts confirmation
- Dealer B attempts confirmation simultaneously

The first transaction acquires the row lock and updates inventory.

The second transaction waits until the first completes, preventing overselling and negative inventory.

### Isolation Assumptions

The implementation relies on database row-level locking through select_for_update() inside transaction.atomic().

This guarantees inventory consistency during concurrent order confirmations.

## Channel Sync Strategy

### Matching Logic

Products are matched using SKU.

The sync process uses update_or_create() to ensure records are updated instead of duplicated.

### Create Flow

If a product from the channel feed does not exist locally:

- Create Product
- Create Inventory

### Update Flow

If a product already exists:

- Update name
- Update category
- Update price
- Update inventory quantity

### Conflict Resolution

The channel feed is treated as the source of truth.

When channel data differs from local data, the channel values overwrite local values.

### Idempotency

The sync process is idempotent.

Running the same feed multiple times:

- Does not create duplicate products
- Updates existing records
- Produces consistent results

This is achieved using Django's update_or_create() method.

## Indexing Strategy

The Product SKU field is marked as unique. Django automatically creates a database index for unique fields, allowing efficient product lookups and synchronization by SKU.

Primary keys on all models are automatically indexed by Django and are used for joins and relationship lookups.

For larger datasets, additional indexes could be added on:

* Order.order_number for faster order retrieval.
* Dealer.dealer_code for dealer searches.
* Product.category for category-based filtering.

The current indexing strategy is sufficient for the expected assignment-scale workload while maintaining simple database design.

## Multi-Tenant Extension

To support multiple dealers or suppliers operating independently, a Tenant model could be introduced.

Each Product, Inventory, Dealer, Order, and OrderItem would be associated with a tenant through a ForeignKey relationship.

Example:

* Tenant A can only access its own products, inventory, and orders.
* Tenant B is isolated from Tenant A's data.

All API queries would be filtered by the authenticated tenant to ensure data isolation.

For larger deployments, a schema-per-tenant or database-per-tenant approach could also be considered, but a shared database with tenant filtering would be the simplest initial implementation.
