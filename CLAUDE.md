# CLAUDE.md - VV-Kaffee E-Commerce Platform

## Project Overview

**VV-Kaffee** (Versöhnung und Vergebung Kaffee) is a Django-based e-commerce platform dedicated to selling ethically sourced Rwandan coffee to customers in Germany. The project celebrates forgiveness, reconciliation, and Rwanda's healing journey.

### Core Technology Stack
- **Backend**: Django 5.2.5, Python 3.12
- **Frontend**: Bootstrap 5, HTML/CSS/JavaScript
- **Database**: SQLite (development), PostgreSQL (production via Heroku)
- **Payment Processing**: Stripe (PaymentIntent API + Webhooks)
- **Authentication**: Django Allauth (email/username login)
- **Media Storage**: Cloudinary
- **PDF Generation**: ReportLab (for picklists and receipts)
- **Deployment**: Heroku with Gunicorn and WhiteNoise
- **Configuration**: python-decouple and python-dotenv

---

## Codebase Structure

```
VV-Kaffee-PP5/
├── cart/                                    # Shopping cart app (session-based)
│   ├── models.py                           # (minimal - cart stored in session)
│   ├── views.py                            # add/update/remove cart items
│   ├── urls.py                             # /cart/* routes
│   ├── context_processors.py               # cart_summary for templates
│   └── templates/cart/
│       └── cart.html                       # cart display page
│
├── orders/                                  # Order & checkout management
│   ├── models.py                           # Order, OrderItem models
│   ├── views.py                            # checkout, order history, fulfillment
│   ├── admin.py                            # customized admin for orders
│   ├── urls.py                             # /checkout/, /orders/*, /fulfillment/*
│   └── templates/orders/
│       ├── checkout.html                   # payment form (Stripe)
│       ├── order_confirmation.html
│       └── fulfillment_panel.html
│
├── products/                                # Product catalog
│   ├── models.py                           # Product, Category models
│   ├── views.py                            # product list, detail, search
│   ├── admin.py                            # product admin with image preview
│   ├── urls.py                             # /shop/*, /products/*
│   ├── fixtures/
│   │   └── sample_products.json           # sample data for products
│   └── templates/products/
│       ├── product_list.html              # paginated product catalog
│       └── product_detail.html            # single product view
│
├── profiles/                                # User profile management
│   ├── models.py                           # Profile model (OneToOne with User)
│   ├── views.py                            # profile edit, dashboard, order history
│   ├── admin.py                            # profile admin
│   ├── urls.py                             # /account/*
│   └── templates/profiles/
│       ├── account_dashboard.html
│       ├── profile_edit.html
│       ├── order_list.html
│       └── order_detail.html
│
├── reviews/                                 # Product reviews & experience feedback
│   ├── models.py                           # ProductReview, ExperienceFeedback
│   ├── views.py                            # review submission, list
│   ├── admin.py                            # review moderation
│   ├── urls.py                             # /reviews/*
│   └── templates/reviews/
│       ├── review_form.html
│       ├── review_list.html
│       └── experience_form.html
│
├── newsletter/                              # Newsletter subscription
│   ├── models.py                           # Subscriber model
│   ├── views.py                            # subscribe/unsubscribe
│   ├── admin.py                            # subscriber management
│   └── urls.py                             # /newsletter/*
│
├── versohnung_und_vergebung_kaffee/        # Main Django project
│   ├── settings.py                         # Django settings (uses decouple)
│   ├── urls.py                             # Root URL configuration
│   ├── wsgi.py                             # WSGI application entry point
│   ├── asgi.py                             # ASGI application entry point
│   └── middleware/
│       └── fulfillment_redirect.py         # Post-login redirect for fulfillment team
│
├── templates/                               # Global templates
│   ├── base.html                           # Base template with nav/footer
│   ├── home.html                           # Homepage
│   ├── 404.html                            # 404 error page
│   ├── 500.html                            # 500 error page
│   └── account/                            # Allauth template overrides
│       ├── login.html
│       └── signup.html
│
├── static/                                  # Static files
│   ├── css/                                # Custom CSS
│   ├── images/                             # Images, logos, branding
│   └── branding/                           # Brand assets
│
├── staticfiles/                             # Collected static files (collectstatic)
├── manage.py                                # Django management script
├── requirements.txt                         # Python dependencies
├── Procfile                                 # Heroku deployment config
├── db.sqlite3                              # Local SQLite database
├── db.json                                 # Database fixture/export
└── README.md                                # Project documentation
```

---

## Django Apps & Responsibilities

### 1. **cart/** - Shopping Cart
- **Purpose**: Session-based shopping cart
- **Key Features**:
  - Add/remove products to cart
  - Update quantities
  - Store grind preferences (whole beans, espresso, filter, french press)
  - Calculate subtotal
- **Models**: None (cart stored in `request.session`)
- **Context Processor**: `cart_summary()` makes cart available in all templates

### 2. **orders/** - Order Processing & Fulfillment
- **Purpose**: Handle checkout, payment, and order management
- **Key Models**:
  - `Order`: Customer orders with status tracking
  - `OrderItem`: Individual line items in orders
- **Statuses**: `new`, `pending_fulfillment`, `paid`, `fulfilled`, `cancelled`, `refunded`
- **Key Features**:
  - Stripe PaymentIntent integration
  - Webhook handling for payment confirmation
  - Order history for customers
  - Fulfillment panel for staff (requires permissions)
  - Picklist PDF generation
  - Email notifications
- **Permissions**:
  - `view_fulfillment`: Access to fulfillment panel
  - `change_fulfillment_status`: Mark orders as fulfilled

### 3. **products/** - Product Catalog
- **Purpose**: Manage coffee products and categories
- **Key Models**:
  - `Product`: Coffee products with detailed attributes
  - `Category`: Product categorization
- **Product Attributes**:
  - Basic: name, SKU, price, weight (grams), stock, image
  - Coffee-specific: origin, farm, variety, altitude, process, roast type, tasting notes
  - Available grinds: whole, espresso, filter, french_press
- **Key Features**:
  - Paginated product listing
  - Product detail pages with reviews
  - Stock tracking
  - Image upload (Cloudinary)
  - Auto-generated slugs

### 4. **profiles/** - User Profiles
- **Purpose**: User profile management and order history
- **Key Model**: `Profile` (OneToOne with User)
- **Profile Fields**:
  - Contact: full_name, email, phone
  - Shipping: street, house_number, postcode, city, country
  - Profile image
- **Key Features**:
  - Account dashboard
  - Order history
  - Profile editing
  - Profile image upload
  - Post-login redirect logic

### 5. **reviews/** - Reviews & Feedback
- **Purpose**: Product reviews and overall experience feedback
- **Key Models**:
  - `ProductReview`: Product-specific reviews (1-5 stars)
  - `ExperienceFeedback`: General shopping experience feedback
- **Constraints**: One review per product per user
- **Key Features**:
  - Star ratings (1-5)
  - Review title and comment
  - Review moderation in admin
  - Display on product pages

### 6. **newsletter/** - Newsletter Management
- **Purpose**: Newsletter subscription system
- **Key Model**: `Subscriber`
- **Key Features**:
  - Email subscription
  - Unsubscribe functionality
  - Admin management of subscribers
  - GDPR compliance (double opt-in)

---

## Key Models & Relationships

### Data Model Overview

```
User (Django Auth)
  ├── Profile (1:1)
  ├── Order (1:N)
  ├── ProductReview (1:N)
  └── ExperienceFeedback (1:N)

Category
  └── Product (1:N)
      ├── OrderItem (1:N)
      └── ProductReview (1:N)

Order
  ├── OrderItem (1:N)
  ├── ExperienceFeedback (1:1)
  └── User (N:1, optional)
```

### Order Model Fields
```python
Order:
  - status: new, pending_fulfillment, paid, fulfilled, cancelled, refunded
  - user: ForeignKey to User (nullable for guest checkout)
  - full_name, email, phone_number
  - street, house_number, city, postal_code, country
  - payment_intent_id: Stripe PaymentIntent ID
  - subtotal, shipping, total
  - fulfilled_at: timestamp when order fulfilled
```

### Product Model Fields
```python
Product:
  - name, slug, sku, category
  - origin, farm, variety, altitude_masl, process
  - roast_type: light, medium, dark
  - tasting_notes
  - price, weight_grams, available_grinds
  - stock, is_active
  - image (Cloudinary)
```

---

## Development Workflow

### Setting Up Local Development

1. **Clone and Setup**:
   ```bash
   git clone <repo-url>
   cd VV-Kaffee-PP5
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Variables** - Create `.env` file:
   ```env
   SECRET_KEY=your_django_secret_key
   DEBUG=True

   # Stripe
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...

   # Email (Gmail)
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   DEFAULT_FROM_EMAIL=your_email@gmail.com

   # Cloudinary (optional)
   CLOUDINARY_URL=cloudinary://...

   # Site
   SITE_URL=http://127.0.0.1:8000
   SITE_NAME=VV-Kaffee
   ```

3. **Database Setup**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py loaddata products/fixtures/sample_products.json  # optional
   ```

4. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test products
python manage.py test orders

# Run with verbose output
python manage.py test --verbosity=2
```

Test files are located in each app: `<app>/tests.py`

### Collecting Static Files

```bash
python manage.py collectstatic --noinput
```

---

## Deployment (Heroku)

### Heroku Setup

1. **Create Heroku App**:
   ```bash
   heroku login
   heroku create vv-kaffee-app
   ```

2. **Add PostgreSQL**:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

3. **Set Config Vars**:
   ```bash
   heroku config:set SECRET_KEY=your_secret_key
   heroku config:set DEBUG=False
   heroku config:set STRIPE_PUBLISHABLE_KEY=pk_live_...
   heroku config:set STRIPE_SECRET_KEY=sk_live_...
   heroku config:set EMAIL_HOST_USER=your_email@gmail.com
   heroku config:set EMAIL_HOST_PASSWORD=your_app_password
   heroku config:set CLOUDINARY_URL=cloudinary://...
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

### Procfile
```
web: gunicorn versohnung_und_vergebung_kaffee.wsgi
```

### Production Checklist
- ✅ `DEBUG=False`
- ✅ `ALLOWED_HOSTS` configured
- ✅ PostgreSQL database URL set
- ✅ Static files collected and WhiteNoise configured
- ✅ Stripe live keys configured
- ✅ Email SMTP configured
- ✅ HTTPS enforced
- ✅ Cloudinary for media storage

---

## Stripe Integration

### Payment Flow

1. **Customer initiates checkout** (`orders/views.py`):
   - Cart contents converted to OrderItems
   - Order created with status `new`

2. **Stripe PaymentIntent created**:
   ```python
   stripe.PaymentIntent.create(
       amount=int(order.total * 100),  # cents
       currency='eur',
       metadata={'order_id': order.id}
   )
   ```

3. **Payment processed on frontend**:
   - Stripe.js handles card input
   - Payment confirmed with Stripe

4. **Webhook receives payment confirmation**:
   - Order status updated to `paid`
   - Stock decremented
   - Confirmation email sent

### Webhook Handling
Webhook endpoint: `/orders/stripe-webhook/`

Events handled:
- `payment_intent.succeeded`: Mark order as paid
- `payment_intent.payment_failed`: Mark order as cancelled

### Testing Stripe
Use test card: `4242 4242 4242 4242`, any future expiry, any CVC

---

## Authentication & Authorization

### Django Allauth Configuration

- **Login methods**: Username OR Email
- **Email verification**: Optional (set to `mandatory` in production)
- **Social auth**: Google OAuth configured (can add more providers)

### User Flows

1. **Registration**: `/accounts/signup/`
2. **Login**: `/accounts/login/`
3. **Logout**: `/accounts/logout/`
4. **Password reset**: `/accounts/password/reset/`

### Post-Login Redirect
Custom middleware (`FulfillmentPostLoginMiddleware`) redirects:
- Fulfillment team users → `/fulfillment/`
- Regular users → `/account/dashboard/`

### Permissions

**Order Fulfillment**:
- `orders.view_fulfillment`: Access fulfillment panel
- `orders.change_fulfillment_status`: Mark orders as fulfilled

**Groups**:
- Create "Fulfillment Team" group in admin
- Assign fulfillment permissions to group
- Add staff users to group

---

## Email Configuration

### Gmail SMTP Setup

1. **Enable 2FA** on Gmail account
2. **Generate App Password**: Google Account → Security → App Passwords
3. **Set environment variables**:
   ```env
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_16_char_app_password
   DEFAULT_FROM_EMAIL=your_email@gmail.com
   ```

### Email Templates

Emails sent on:
- ✅ Order placed (pending payment)
- ✅ Payment confirmed
- ✅ Order fulfilled
- ⚠️ Order cancelled (TODO: not yet implemented)

Email templates should be created in: `templates/orders/email/`

---

## Common Tasks for AI Assistants

### 1. Adding a New Product

```python
# Via Django shell
python manage.py shell

from products.models import Product, Category

category = Category.objects.get(name="Coffee Beans")
product = Product.objects.create(
    name="Gitesi Natural",
    sku="GITESI-250",
    category=category,
    price=12.90,
    weight_grams=250,
    origin="Rwanda",
    farm="Gitesi Washing Station",
    variety="Bourbon",
    roast_type="medium",
    tasting_notes="Berry, chocolate, citrus",
    available_grinds="whole,espresso,filter",
    stock=50,
    is_active=True
)
```

### 2. Testing Order Flow

```python
# Create test order
from orders.models import Order, OrderItem
from products.models import Product
from django.contrib.auth.models import User

user = User.objects.first()
product = Product.objects.first()

order = Order.objects.create(
    user=user,
    full_name="Test User",
    email="test@example.com",
    street="Teststrasse",
    house_number="42",
    city="Berlin",
    postal_code="10115",
    country="Germany"
)

OrderItem.objects.create(
    order=order,
    product=product,
    product_name_snapshot=product.name,
    unit_price=product.price,
    quantity=2,
    grind="whole",
    weight_grams=product.weight_grams
)

order.recalc_totals()
```

### 3. Creating Fulfillment User

```bash
python manage.py shell

from django.contrib.auth.models import User, Group, Permission

# Create group
fulfillment_group, created = Group.objects.get_or_create(name="Fulfillment Team")

# Add permissions
perms = Permission.objects.filter(
    codename__in=['view_fulfillment', 'change_fulfillment_status']
)
fulfillment_group.permissions.set(perms)

# Create user and add to group
user = User.objects.create_user('fulfillment_user', 'user@example.com', 'password')
user.groups.add(fulfillment_group)
```

### 4. Debugging Cart Issues

```python
# View session cart
from django.contrib.sessions.models import Session
session = Session.objects.latest('expire_date')
session.get_decoded()  # Look for 'cart' key
```

### 5. Bulk Stock Update

```python
from products.models import Product

# Add 10 stock to all products
Product.objects.filter(is_active=True).update(stock=models.F('stock') + 10)
```

---

## Code Conventions & Best Practices

### 1. **Model Naming**
- Use singular names: `Product`, `Order`, `Category`
- Related names use plural: `related_name="products"`

### 2. **URL Naming**
- Use namespaces: `products:product_list`, `cart:view_cart`
- Use hyphens in URLs: `/order-history/`, `/product-detail/`

### 3. **View Patterns**
- Function-based views for simple CRUD
- Class-based views for complex logic
- Always use `@login_required` for authenticated views
- Use `@permission_required` for staff-only views

### 4. **Template Organization**
- App templates: `<app>/templates/<app>/template.html`
- Global templates: `templates/template.html`
- Extend `base.html` for consistent layout

### 5. **Static Files**
- Custom CSS: `static/css/`
- Images: `static/images/`
- Use `{% load static %}` and `{% static 'path' %}`

### 6. **Forms**
- Use `django-widget-tweaks` for Bootstrap styling
- Always include CSRF token: `{% csrf_token %}`

### 7. **Security**
- Never commit `.env` files
- Use `python-decouple` for config
- Always use HTTPS in production
- Validate user input
- Use Django's built-in protection (CSRF, XSS, SQL injection)

### 8. **Testing**
- Write tests for all new features
- Test models, views, and forms
- Use fixtures for test data
- Mock external services (Stripe, email)

### 9. **Git Workflow**
- Create feature branches: `feature/add-wishlist`
- Meaningful commit messages: "Add wishlist functionality to user profile"
- PR reviews before merging
- Keep main branch deployable

---

## Database Management

### Migrations

```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Rollback migration
python manage.py migrate <app_name> <migration_number>
```

### Fixtures (Data Import/Export)

```bash
# Export data
python manage.py dumpdata products.Product --indent 2 > products/fixtures/products.json

# Import data
python manage.py loaddata products/fixtures/products.json
```

### Database Reset (Development Only)

```bash
# WARNING: Deletes all data!
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## Known Issues & TODOs

### Current Known Bugs (from README)
1. ⚠️ **Admin panel product image preview**: Images may not display immediately; refresh needed
2. 🕐 **Order stock conflicts**: Race condition possible with simultaneous orders
3. 📧 **Cancellation email not sent**: Users don't receive cancellation confirmation
4. 📆 **Date/time picker inconsistencies**: Mobile browser compatibility issues
5. 📱 **Product layout on small screens**: Layout issues on very narrow devices

### Planned Features (from README)
- 📨 Order cancellation emails
- 🌐 Multilingual support (English, French)
- 🗓️ Admin calendar view for orders
- ⚙️ Preferred product selection for returning customers
- 📅 Store opening hours display
- 🗺️ Interactive map for coffee origins
- 💳 Enhanced payment options (PayPal)
- 🥘 Updated branding

---

## Debugging & Troubleshooting

### Common Issues

**1. Stripe webhook not working locally**:
```bash
# Use Stripe CLI
stripe listen --forward-to localhost:8000/orders/stripe-webhook/
```

**2. Static files not loading**:
```bash
python manage.py collectstatic --noinput
# Check STATIC_ROOT and STATIC_URL in settings.py
```

**3. Email not sending**:
- Check Gmail App Password is correct
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env
- Check EMAIL_TIMEOUT setting

**4. Cart not persisting**:
- Check session middleware is enabled
- Verify CSRF token in forms
- Check browser cookies enabled

**5. Image upload failing**:
- Check CLOUDINARY_URL is set
- Verify Cloudinary credentials
- Check file size limits

### Logging

Check logs in Heroku:
```bash
heroku logs --tail
```

Django logs to console (INFO level by default in settings.py)

---

## Important Files Reference

### Configuration Files
- `versohnung_und_vergebung_kaffee/settings.py` - Django settings
- `.env` - Environment variables (NOT committed)
- `requirements.txt` - Python dependencies
- `Procfile` - Heroku deployment config

### Key Python Files
- `versohnung_und_vergebung_kaffee/urls.py` - Root URL config
- `orders/views.py` - Checkout and Stripe integration
- `cart/context_processors.py` - Cart availability in templates
- `profiles/views.py` - Post-login redirect logic

### Templates
- `templates/base.html` - Base template with nav/footer
- `templates/home.html` - Homepage
- `cart/templates/cart/cart.html` - Shopping cart
- `orders/templates/orders/checkout.html` - Stripe payment form

### Static Files
- `static/css/` - Custom styles
- `static/images/` - Site images
- `static/branding/` - Logo and brand assets

---

## Working with AI Assistants - Guidelines

### What to Expect from AI Assistants

When working on this codebase, AI assistants should:

1. **Always read files before modifying** - Never propose changes to code you haven't read
2. **Follow Django best practices** - Use Django's built-in features (ORM, forms, auth)
3. **Maintain consistency** - Follow existing code patterns and naming conventions
4. **Test changes** - Run tests after modifications
5. **Consider security** - Watch for XSS, SQL injection, CSRF vulnerabilities
6. **Avoid over-engineering** - Keep solutions simple and focused
7. **Use migrations properly** - Always create migrations after model changes
8. **Respect git workflow** - Create feature branches, meaningful commits

### Common AI Assistant Tasks

**Good tasks to request**:
- ✅ Add new product features (fields, filters, sorting)
- ✅ Extend order management (new statuses, notifications)
- ✅ Create new views and templates
- ✅ Write tests for existing functionality
- ✅ Debug specific issues
- ✅ Improve admin interface
- ✅ Add validation to forms
- ✅ Optimize database queries
- ✅ Fix accessibility issues

**Tasks requiring caution**:
- ⚠️ Modifying Stripe integration (test thoroughly)
- ⚠️ Changing authentication flow (security implications)
- ⚠️ Database schema changes (requires migrations)
- ⚠️ Modifying payment calculation logic
- ⚠️ Changing email templates (affects user communication)

### AI Assistant Best Practices

1. **Start with exploration**: Read relevant files first
2. **Plan before coding**: Outline approach before implementation
3. **Make incremental changes**: Small, testable changes over large refactors
4. **Test immediately**: Run tests after each significant change
5. **Document changes**: Update CLAUDE.md if architecture changes
6. **Ask for clarification**: When requirements are unclear
7. **Consider edge cases**: Think about error scenarios
8. **Maintain backwards compatibility**: Don't break existing functionality

---

## Quick Reference Commands

```bash
# Development
python manage.py runserver
python manage.py shell
python manage.py test
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic

# Data
python manage.py loaddata <fixture_file>
python manage.py dumpdata <app.Model> --indent 2 > fixture.json

# Heroku
heroku logs --tail
heroku run python manage.py migrate
heroku run python manage.py shell
heroku config:set KEY=value
git push heroku main

# Stripe CLI (local webhook testing)
stripe listen --forward-to localhost:8000/orders/stripe-webhook/
```

---

## Contact & Support

- **GitHub**: [Vinsengi/VV-Kaffee-PP5](https://github.com/Vinsengi/VV-Kaffee-PP5)
- **Live Site**: [vv-kaffee-5b7b3eb05052.herokuapp.com](https://vv-kaffee-5b7b3eb05052.herokuapp.com/)
- **Documentation**: README.md for user-facing docs

---

**Last Updated**: 2025-12-04
**Django Version**: 5.2.5
**Python Version**: 3.12
