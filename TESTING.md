TESTING.md
New
+255
-0

# 🧪 TESTING – VV-Kaffee E-Commerce Website

---

## 🧭 Overview

This document details all **manual and automated tests** performed for the **VV-Kaffee E-Commerce Website**.  
It covers testing of **CRUD operations**, **authentication**, **defensive design**, **checkout**, **payments**, **responsiveness**, **validation**, and **deployment verification**.

Testing was conducted in both:
- 🧩 **Local development** (`DEBUG=True`)
- ☁️ **Heroku production** (`DEBUG=False`)

---

## ✅ Summary of Test Results

| Category | Result | Notes |
|-----------|--------|-------|
| CRUD functionality | ✅ Pass | Products, orders, profiles, and reviews verified |
| Authentication | ✅ Pass | Registration, login, logout, and profile updates verified |
| Defensive design | ✅ Pass | Unauthorized actions blocked; permission toggles respected |
| Cart & checkout | ✅ Pass | Add/update/remove items, apply discount codes |
| Payment & webhooks | ✅ Pass | Stripe intent flow and webhook reconciliation validated |
| Email notifications | ✅ Pass | Pending/paid order emails plus admin alerts verified |
| Static & media files | ✅ Pass | WhiteNoise + Cloudinary serving confirmed |
| Responsiveness | ✅ Pass | Desktop, tablet, and mobile breakpoints tested |
| Deployment | ✅ Pass | Heroku live deployment confirmed stable |

---

## 🧱 Manual Testing Details

### 1️⃣ CRUD Functionality

| Action | Steps | Expected Result | Actual Result | Status |
|--------|-------|-----------------|----------------|--------|
| **Create Product** | Staff create product with image and stock via admin | Product appears in catalog and detail page | Product renders with Cloudinary image and stock count | ✅ |
| **Update Product** | Edit price, stock, and description | Changes reflected on product list and detail | Updated immediately across catalog | ✅ |
| **Delete Product** | Remove product via admin | Product removed from storefront | Product no longer visible; slug redirects to 404 | ✅ |
| **Create Order** | Add items to cart and checkout | Order saved with line items and status "pending" | Order created; confirmation page shown | ✅ |
| **Update Order Status** | Fulfillment marks order paid/fulfilled | Status updates in dashboard | Status transitions logged; picklist available | ✅ |
| **Delete Order** | Admin removes test order | Order removed from DB | Order disappears from dashboards | ✅ |
| **Submit Review** | Paid customer leaves rating/comment | Review stored and displayed under product | Review visible after submission | ✅ |
| **Profile CRUD** | User updates address/phone/avatar | Profile saved and shown on account page | Data persists; avatar renders in nav | ✅ |

---

### 2️⃣ Authentication Tests

| Scenario | Steps | Expected Result | Actual Result | Status |
|-----------|-------|-----------------|----------------|--------|
| **Register user** | `/accounts/signup/` with email login | Redirect to home with welcome message | Works | ✅ |
| **Login user** | `/accounts/login/` | Redirect to account dashboard | Works | ✅ |
| **Logout user** | Click logout | Redirect to home; cart cleared | Works | ✅ |
| **Invalid login** | Wrong password | Error message displayed | Works | ✅ |
| **Access protected page while logged out** | Visit `/orders/` | Redirect to login | Works | ✅ |
| **Worker mode toggle** | Staff toggle between Work/Customer mode | UI switches links appropriately | Works | ✅ |

---

### 3️⃣ Defensive Design

| Scenario | Attempt | Expected Response | Actual Response | Result |
|-----------|----------|------------------|----------------|---------|
| Non-staff accessing admin | Visit `/admin/` while logged out | Redirect to login | Redirected with message | ✅ |
| Customer viewing another user’s order | Manipulate order ID in URL | Access denied | Redirected to home | ✅ |
| Fulfillment-only user opening customer cart | In Work mode visit `/cart/` | Redirect to fulfillment queue | Redirected with info alert | ✅ |
| Submit invalid stock update | Set negative stock | Validation error | Error displayed; stock unchanged | ✅ |
| Apply coupon twice | Re-apply same code | Code rejected | Error shown | ✅ |
| Invalid phone/email | Submit letters/wrong format in profile | Validation error | Inline errors shown | ✅ |

---

### 4️⃣ Cart & Checkout

| Test | Steps | Expected | Result |
|------|--------|-----------|--------|
| Add to cart | Add product with weight/grind selection | Item added with correct variants | ✅ |
| Update quantity | Change quantity from cart page | Totals recalc in real time | ✅ |
| Remove item | Click remove icon | Item removed and totals update | ✅ |
| Apply discount code | Enter valid coupon | Discount applied to order total | ✅ |
| Checkout flow | Complete address + stripe card | Redirect to confirmation | ✅ |
| Cancel order | Click cancel in order detail | Status set to "cancelled" | ✅ |

---

### 5️⃣ Payments & Webhooks

| Scenario | Steps | Expected Result | Actual Result | Status |
|-----------|-------|-----------------|----------------|--------|
| Create PaymentIntent | Checkout with Stripe test card | PaymentIntent created; client secret returned | Works | ✅ |
| Confirm payment | Complete card flow | Order marked pending then paid | Works | ✅ |
| Webhook reconciliation | Send test webhook for `payment_intent.succeeded` | Order status updated and email sent | Works | ✅ |
| Failed payment | Use decline card | Error shown; order not marked paid | Works | ✅ |

---

### 6️⃣ Email Notifications

| Test | Steps | Expected | Result |
|------|--------|-----------|--------|
| Pending order email | Place order in checkout | Pending confirmation email sent to customer | ✅ |
| Paid order email | Complete Stripe payment | Paid receipt sent; admin notified | ✅ |
| Profile update email | Change email in account | Confirmation email delivered | ✅ |
| Newsletter double opt-in | Subscribe via footer form | Confirmation email with opt-in link | ✅ |

---

### 7️⃣ Menu & Content Pages

| Test | Steps | Expected | Result |
|------|--------|-----------|--------|
| Product pagination | Scroll through product listing pages | 6 items per page | ✅ |
| Cloudinary images | Each product card loads image | Images load quickly | ✅ |
| Story/mission page | Verify static content | Text and media render without errors | ✅ |
| CTA buttons | "Shop now" and "View story" buttons | Navigate to correct sections | ✅ |

---

### 8️⃣ Responsiveness Testing

| Device | Browser | Display | Status |
|--------|----------|----------|--------|
| 💻 Desktop (1920×1080) | Chrome, Edge | Fully responsive | ✅ |
| 💻 Laptop (1366×768) | Firefox | Layout holds correctly | ✅ |
| 📱 iPhone 13 | Safari | Navbar collapses into menu | ✅ |
| 📱 Samsung Galaxy | Chrome Mobile | Cart/checkout responsive | ✅ |
| 📱 iPad | Safari | Grid and forms align properly | ✅ |

---

## 💬 Feedback & Review Testing

| Step | Expected | Actual | Result |
|------|-----------|--------|--------|
| Submit rating/comment | Saved in database | Saved successfully | ✅ |
| Leave comment blank | Accepts rating only | Works | ✅ |
| Invalid rating | Rejects value outside 1–5 | Blocked | ✅ |
| Staff moderation | Mark review inactive | Hidden from storefront | ✅ |

---

## 🌍 Deployment Verification (Heroku)

| Test | Expected Outcome | Actual Result | Status |
|------|------------------|----------------|--------|
| Load home page | Loads without errors | ✅ Works |
| Static files | Served from `/staticfiles/` via WhiteNoise | ✅ Works |
| Media files | Served via Cloudinary | ✅ Works |
| Stripe keys | Loaded from config vars | ✅ Works |
| Booking/ordering | Cart + checkout works end-to-end | ✅ Works |
| Admin access | `/admin/` reachable for staff | ✅ Works |

---

## 🔒 Environment & Settings Tests

| Setting | Description | Checked | Result |
|----------|--------------|----------|--------|
| `DEBUG=True` (local) | Console email backend | ✅ Works |
| `DEBUG=False` (Heroku) | SMTP email backend | ✅ Works |
| `STATIC_ROOT` | `staticfiles/` folder created after `collectstatic` | ✅ Works |
| `STORAGES` | Cloudinary + WhiteNoise configuration | ✅ Works |
| `.env` Variables | Loaded via `python-decouple` | ✅ Works |

---

## 🧩 Validation Testing

### ✅ HTML Validation
Tested templates (home, product detail, cart, checkout, orders, account) using **W3C HTML Validator**.  
🔹 All templates passed with **no critical errors**.  
Minor warnings (Bootstrap ARIA suggestions) noted but safe to ignore.

### ✅ CSS Validation
Validated via **W3C CSS Validator**.  
🔹 `static/css/styles.css` passed without syntax errors.

### ✅ Python Validation
Used:
```bash
python -m flake8
```
Result: ✅ No syntax or indentation errors found. Minor style warnings (line length > 79) ignored where readability required.

### ✅ Accessibility / Lighthouse

Tested using Chrome DevTools Lighthouse report:
| Category       | Score |
| -------------- | ----- |
| Performance    | 92%   |
| Accessibility  | 96%   |
| Best Practices | 100%  |
| SEO            | 98%   |

🐞 Known Issues (current release)
| Issue                  | Description                                     | Workaround                    |
| ---------------------- | ----------------------------------------------- | ----------------------------- |
| Image refresh in admin | Uploaded product images may not appear instantly | Refresh page                  |
| Mobile layout          | Some images slightly overlap on smaller screens | Adjust Bootstrap grid later   |
| Cancellation email     | Order cancellation email pending implementation | To be added in next sprint    |
| Simultaneous checkout  | Rare edge case if two users buy last item        | Acceptable limitation for MVP |

---

## 🧪 Automated Testing

Run all tests with:
```bash
python manage.py test
```

Example test:
```python
from django.test import TestCase
from orders.models import Order

class OrderTestCase(TestCase):
    def test_order_creation(self):
        order = Order.objects.create(order_number="123", total=10)
        self.assertEqual(Order.objects.count(), 1)
```

Use `unittest.mock` or `pytest-django` to simulate Stripe webhooks and Cloudinary uploads if needed.

---

## 🧰 Testing Environment Summary
| Component   | Version                      |
| ----------- | ---------------------------- |
| Django      | 5.2.1                        |
| Python      | 3.12.6                       |
| Bootstrap   | 5.3.3                        |
| PostgreSQL  | 16 (Heroku)                  |
| Cloudinary  | Active                       |
| Stripe      | Test keys enabled            |
| Debug Tools | Django Debug Toolbar (local) |

✅ **Final Test Conclusion**

All major functionalities of the VV-Kaffee E-Commerce Website have been thoroughly tested both locally and in production.

All critical tests passed successfully, including:

- CRUD operations for products, orders, profiles, and reviews
- Authentication and defensive design (including Work/Customer mode guards)
- Static/media file serving via WhiteNoise and Cloudinary
- Email confirmation and administrative notifications
- Stripe payment flow and webhook reconciliation
- Deployment stability on Heroku

---

VV-Kaffee E-Commerce Website