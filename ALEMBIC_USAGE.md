# Alembic Database Migrations Guide

This guide explains how to use Alembic for database migrations in Proxie.

---

## Setup

Alembic is already configured and ready to use. The configuration files are:

- `alembic.ini` - Alembic configuration
- `alembic/env.py` - Environment setup (connects to Proxie models)
- `alembic/versions/` - Migration scripts directory

---

## Common Commands

### Create a New Migration

**Auto-generate from model changes:**
```bash
alembic revision --autogenerate -m "Description of changes"
```

**Create empty migration (for data migrations or custom SQL):**
```bash
alembic revision -m "Description of changes"
```

### Apply Migrations

**Apply all pending migrations:**
```bash
alembic upgrade head
```

**Apply migrations up to a specific revision:**
```bash
alembic upgrade <revision_id>
```

**Apply next migration:**
```bash
alembic upgrade +1
```

### Rollback Migrations

**Rollback one migration:**
```bash
alembic downgrade -1
```

**Rollback to a specific revision:**
```bash
alembic downgrade <revision_id>
```

**Rollback all migrations:**
```bash
alembic downgrade base
```

### Check Migration Status

**Show current migration status:**
```bash
alembic current
```

**Show migration history:**
```bash
alembic history
```

**Show pending migrations:**
```bash
alembic heads
```

---

## Workflow Examples

### Adding a New Model

1. **Create the model** in `src/platform/models/`
2. **Import it** in `alembic/env.py` (if not already imported)
3. **Generate migration:**
   ```bash
   alembic revision --autogenerate -m "Add new model"
   ```
4. **Review the generated migration** in `alembic/versions/`
5. **Apply migration:**
   ```bash
   alembic upgrade head
   ```

### Adding a Column

1. **Modify the model** in `src/platform/models/`
2. **Generate migration:**
   ```bash
   alembic revision --autogenerate -m "Add column to table"
   ```
3. **Review and apply:**
   ```bash
   alembic upgrade head
   ```

### Adding Indexes

1. **Create migration:**
   ```bash
   alembic revision -m "Add indexes"
   ```
2. **Edit migration file** to add index operations:
   ```python
   def upgrade():
       op.create_index('idx_name', 'table_name', ['column'])
   ```
3. **Apply migration:**
   ```bash
   alembic upgrade head
   ```

---

## Migration Best Practices

### 1. Always Review Auto-Generated Migrations

Auto-generated migrations may not always be correct:
- Check for unintended changes
- Verify data type changes
- Ensure indexes are correct

### 2. Test Migrations

**Test upgrade:**
```bash
alembic upgrade head
```

**Test downgrade:**
```bash
alembic downgrade -1
alembic upgrade head
```

### 3. Use Descriptive Messages

```bash
# Good
alembic revision -m "Add email verification to providers"

# Bad
alembic revision -m "Update"
```

### 4. Handle Data Migrations

For data migrations (not just schema changes):

```python
def upgrade():
    # Schema change
    op.add_column('providers', sa.Column('verified', sa.Boolean()))
    
    # Data migration
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE providers SET verified = false WHERE verified IS NULL")
    )

def downgrade():
    op.drop_column('providers', 'verified')
```

### 5. Backward Compatibility

When possible, make migrations backward compatible:
- Add columns as nullable first
- Add default values
- Migrate data before removing columns

---

## Existing Migrations

### 001_add_indexes

**Purpose:** Add database indexes for query optimization

**Includes:**
- Single column indexes (clerk_id, status, email, created_at)
- Foreign key indexes (consumer_id, provider_id, request_id)
- Composite indexes (consumer_id + status, etc.)

**To apply:**
```bash
alembic upgrade head
```

**To rollback:**
```bash
alembic downgrade -1
```

---

## Troubleshooting

### Migration Conflicts

If migrations conflict:
1. Check current state: `alembic current`
2. Check history: `alembic history`
3. Resolve conflicts manually in migration files
4. Mark as resolved: `alembic stamp head`

### Database Out of Sync

If database is out of sync with migrations:
1. Check current state: `alembic current`
2. Check database schema manually
3. Create a new migration to sync: `alembic revision --autogenerate`
4. Or stamp current state: `alembic stamp <revision>`

### Import Errors

If you get import errors:
1. Ensure all models are imported in `alembic/env.py`
2. Check that `sys.path` includes project root
3. Verify Python path: `python -c "import src.platform.models"`

---

## CI/CD Integration

### Pre-Deployment

```bash
# Check for pending migrations
alembic check

# Show what would be applied
alembic upgrade head --sql
```

### Deployment

```bash
# Apply migrations
alembic upgrade head
```

### Rollback Plan

```bash
# Rollback if needed
alembic downgrade -1
```

---

## Environment Variables

Alembic uses the same database URL as the application:

```bash
DATABASE_URL=postgresql://user:pass@localhost/proxie_db
```

This is configured in `alembic/env.py` via `settings.DATABASE_URL`.

---

## Notes

- Migrations are version controlled (commit them to git)
- Never edit existing migrations (create new ones instead)
- Test migrations on staging before production
- Keep migrations small and focused
- Document complex migrations in comments
