# ✅ VALIDATION – VV-Kaffee Online Shop

---

## 🧭 Overview

This document captures validation evidence for **VV-Kaffee Online Shop**, confirming compliance with web standards and best practices.
All checks reference the latest deployed version on Heroku:

🔗 https://vv-kaffee-5b7b3eb05052.herokuapp.com/

---

## 🧩 HTML Validation

**Tool Used:** [W3C HTML Validator](https://validator.w3.org/nu/)

**Pages Tested:**
- Home page (`/`)

    ![Home page HTML validation – passed](./static/images/validation/html_validation/home_page_valid.png)

- Products list (`/products/`)

    ![Products list HTML validation – passed](./static/images/validation/html_validation/products_page_valid.png)

- Product detail (`/products/<slug>/`)

    ![Product detail HTML validation – passed](./static/images/validation/html_validation/product_detail_valid.png)

- Cart (`/cart/`)

    ![Cart page HTML validation – passed](./static/images/validation/html_validation/cart_page_valid.png)

- Checkout (`/checkout/`)

    ![Checkout page HTML validation – passed](./static/images/validation/html_validation/checkout_page_valid.png)

- User profile (`/profiles/`)

    ![Profile page HTML validation – passed](./static/images/validation/html_validation/profile_page_valid.png)

- Login (`/accounts/login/`)

    ![Login page HTML validation – passed](./static/images/validation/html_validation/login_page_valid.png)

**Result:** ✅ **Passed**

**Notes:**
- No syntax or structural errors detected on validated pages.
- All templates render HTML5-compliant markup.

---

## 🎨 CSS Validation

**Tool Used:** [W3C CSS Validator](https://jigsaw.w3.org/css-validator/)

**File Validated:**
- `/static/css/site.css`

    ![Site stylesheet validated](./static/images/validation/css_validation/site_css_validated.png)

**Result:** ✅ **No errors found**

**Notes:**
- Stylesheet free of invalid declarations and duplicate selectors.

---

## Lighthouse Checks

**Accessibility Checks using Chrome DevTools Lighthouse**

- Home page accessibility

    ![Home page Lighthouse results](./static/images/validation/lighthouse_validation/home_page_lighthouse.png)

- Products list accessibility

    ![Products list Lighthouse results](./static/images/validation/lighthouse_validation/products_page_lighthouse.png)

- Product detail accessibility

    ![Product detail Lighthouse results](./static/images/validation/lighthouse_validation/product_detail_lighthouse.png)

- Checkout accessibility

    ![Checkout Lighthouse results](./static/images/validation/lighthouse_validation/checkout_page_lighthouse.png)

- Profile accessibility (logged-in users)

    ![Profile Lighthouse results](./static/images/validation/lighthouse_validation/profile_page_lighthouse.png)

♿ Accessibility

Chrome DevTools Lighthouse (Desktop & Mobile)

| Category           | Score | Notes                                                 |
| ------------------ | ----- | ----------------------------------------------------- |
| **Performance**    | > 90% | Static assets served via Whitenoise and Cloudinary    |
| **Accessibility**  | > 90% | Semantic HTML, ARIA labels, and focus styles applied  |
| **Best Practices** | > 90% | HTTPS enforced, secure links, clean console           |
| **SEO**            | > 90% | Titles, meta descriptions, and sitemap present        |

---

## 🐍 Python / PEP8 Validation

**Tools Used:**
- `flake8`
- `pycodestyle`

**Command:**
```bash
python -m flake8
```

**Files Tested:**
- `products/` (models, forms, views)
- `cart/` (contexts, forms, views)
- `orders/` (models, views, webhooks)
- `newsletter/forms.py`
- `profiles/models.py`
- `versohnung_und_vergebung_kaffee/settings.py`

**Result:** ✅ All files passed

**Notes:**
- No syntax, indentation, or import errors found.
- Line-length warnings addressed or ignored only where longer query chains improve readability.

---

## 🌐 Responsiveness Validation

**Tool Used:** Chrome DevTools Responsive Viewer

| Device             | Resolution | Result       |
| ------------------ | ---------- | ------------ |
| Desktop            | 1920×1080  | ✅ Responsive |
| Laptop             | 1366×768   | ✅ Responsive |
| iPad               | 768×1024   | ✅ Responsive |
| iPhone 13          | 390×844    | ✅ Responsive |
| Samsung Galaxy S22 | 412×915    | ✅ Responsive |

✅ Layouts adjust with the Bootstrap 5 grid and flex utilities. No horizontal scroll or overlapping elements observed.

---

## ✅ Additional Checks

| Test                           | Expected                             | Result |
| ------------------------------ | ------------------------------------ | ------ |
| Heroku app loads without error | Page served successfully             | ✅ Pass |
| Static files load correctly    | Served via Whitenoise & Cloudinary   | ✅ Pass |
| Payment flow                   | Stripe checkout completes            | ✅ Pass |
| Order emails                   | Pending and paid notifications send  | ✅ Pass |
| HTTPS enforced                 | All routes redirect securely         | ✅ Pass |

---

## 🧾 Summary

| Validation Type | Tool Used            | Result |
| --------------- | -------------------- | ------ |
| HTML            | W3C Markup Validator | ✅ Pass |
| CSS             | W3C CSS Validator    | ✅ Pass |
| Python          | Flake8 / Pycodestyle | ✅ Pass |
| Accessibility   | Lighthouse           | ✅ Pass |
| Responsiveness  | Chrome DevTools      | ✅ Pass |
| Deployment      | Heroku / Cloudinary  | ✅ Pass |

