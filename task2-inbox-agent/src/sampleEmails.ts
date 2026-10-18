import { CustomerEmail, EmailCategory } from "./types";

const entries: Array<[string, string, string, string]> = [
  ["Asha Rao", "Website colors look different", "The colors on my homepage don't match the theme settings. How can I customize them?", "technical"],
  ["Rahul Mehta", "Custom font question", "I want to change the fonts on my directory website. Where should I start?", "technical"],
  ["Priya Shah", "Domain setup help", "I connected a domain but my website is not showing the expected page. What should I check?", "technical"],
  ["Daniel Brooks", "Page template issue", "A page template looks broken after I edited it. Can you point me to the relevant setup guide?", "technical"],
  ["Neha Kapoor", "Members cannot see a page", "A page that should be visible to members is not appearing for them. How do I investigate?", "technical"],
  ["Arjun Nair", "Email notification settings", "I need to review the email notifications sent by my website. Where are these configured?", "technical"],
  ["Fatima Ali", "Homepage customization", "How can I customize the layout and appearance of the homepage?", "technical"],
  ["Kiran Reddy", "Dashboard error", "I receive an error when opening a dashboard page. It worked yesterday.", "technical"],
  ["Olivia Green", "Site is down", "Our entire website is down and customers cannot access it. Please help urgently.", "technical"],
  ["Vikram Singh", "Images not displaying", "The images on one of my pages are not displaying correctly. What should I check?", "technical"],
  ["Meera Iyer", "Change navigation menu", "I would like to update the navigation menu on my website. Is there documentation for this?", "technical"],
  ["Noah Wilson", "Website loading slowly", "My website has been loading very slowly since this morning. Can someone investigate?", "technical"],
  ["Sana Khan", "Configure general settings", "I am setting up a new directory website and need help finding the general settings.", "technical"],
  ["Ethan Clark", "Broken page after edit", "A page stopped working after I changed its content. I need help identifying the cause.", "technical"],
  ["Divya Menon", "Custom domain question", "Can you explain the documented steps for connecting a live domain name?", "technical"],
  ["Rohan Das", "Unable to log in", "I cannot log in to my account even though I believe my password is correct.", "account"],
  ["Grace Lee", "Password reset", "I need to reset my password. What is the recommended process?", "account"],
  ["Imran Sheikh", "Account may be compromised", "I noticed a login I don't recognize and think someone accessed my account.", "security"],
  ["Chloe Martin", "Change account email", "I want to update the email address associated with my account. How should I proceed?", "account"],
  ["Aditya Bose", "Verification code problem", "I am not receiving the verification code needed to access my account.", "account"],
  ["Sara Ahmed", "Locked out of account", "My account access appears to be locked. Can you help me understand what to do?", "account"],
  ["Jacob Miller", "Unauthorized account access", "Someone may have accessed my account without permission. Please treat this as urgent.", "security"],
  ["Ananya Joshi", "Update profile information", "I need to change my profile details but cannot find the right settings.", "account"],
  ["Ben Turner", "Two-factor login issue", "My two-factor authentication code is not working and I cannot access my account.", "account"],
  ["Pooja Verma", "Account access after device change", "I changed phones and can no longer complete the account verification process.", "account"],
  ["Liam Scott", "Invoice request", "Could you help me locate an invoice for my recent subscription payment?", "billing"],
  ["Nisha Gupta", "Charged twice", "My card appears to have been charged twice for the same subscription. Please review this.", "billing"],
  ["Amir Hussain", "Refund request", "I would like to request a refund for a recent payment. Can you confirm whether I qualify?", "billing"],
  ["Emma Davis", "Unexpected subscription charge", "I noticed a charge I don't recognize on my statement. Please investigate.", "billing"],
  ["Suresh Kumar", "Update payment details", "I need to update the payment method used for my subscription.", "billing"],
  ["Maya Patel", "Subscription renewal question", "When I look at my statement, I see a subscription renewal I wasn't expecting.", "billing"],
  ["Oscar White", "Payment dispute", "I dispute this charge and may contact my bank if it cannot be resolved.", "billing"],
  ["Ishita Roy", "Receipt for accounting", "Our finance team needs a receipt for the last payment. Where can we obtain it?", "billing"],
  ["Nathan Hall", "Plan cancellation", "I want to understand the process for cancelling my current subscription.", "billing"],
  ["Kavya Rao", "Invoice details incorrect", "The billing details on my invoice appear incorrect. Please have someone review them.", "billing"],
  ["George Adams", "Pricing information", "Could you tell me where to find information about available plans and pricing?", "sales"],
  ["Ritika Sen", "Request a product demo", "Our company is considering the platform. Is it possible to arrange a demo?", "sales"],
  ["Sam Carter", "Upgrade options", "We may need a larger plan as our directory grows. Where can I review the options?", "sales"],
  ["Tara Krishnan", "New business inquiry", "I am evaluating directory software for a new business and would like more information.", "sales"],
  ["Felix Young", "Trial availability", "I would like to know whether a trial is available before making a purchasing decision.", "sales"],
  ["Harini Rao", "Enterprise requirements", "We are evaluating the platform for a larger organization and want to discuss our requirements.", "sales"],
  ["Leo Perez", "Request new integration", "It would be helpful to have an integration with our internal CRM. Please consider this feature.", "feature"],
  ["Anjali Pillai", "Feature request for reporting", "Please add more reporting filters so we can analyze directory activity.", "feature"],
  ["Chris Evans", "Bulk editing suggestion", "A bulk-editing feature for member records would save our team a lot of time.", "feature"],
  ["Sneha Kulkarni", "Improved search filters", "I would like to suggest additional search filters for directory visitors.", "feature"],
  ["David King", "API integration request", "Do you plan to add more API integration options? This would help our workflow.", "feature"],
  ["Zoya Mir", "Accessibility improvement", "It would be helpful if more accessibility customization options were available.", "feature"],
  ["Peter Moore", "General question", "I am new to the platform and would appreciate guidance on where to find the official help documentation.", "other"],
  ["Lavanya Rao", "Support feedback", "Thank you for the clear setup resources. I appreciate the help getting started.", "other"],
  ["Michael Reed", "Formal complaint", "I am frustrated that this issue remains unresolved. Please have a support representative review my complaint.", "other"],
  ["Aditi Shah", "Privacy and legal concern", "I have a privacy concern and may seek legal advice. Please escalate this message to the appropriate team.", "other"]
];

const expectedCategoryByLabel: Record<string, EmailCategory> = {
  technical: "technical_support",
  account: "account_management",
  security: "account_management",
  billing: "billing",
  sales: "sales",
  feature: "feature_request",
  other: "other"
};

export const sampleEmailExpectedCategories: EmailCategory[] = entries.map(
  ([, , , expectedLabel]) => expectedCategoryByLabel[expectedLabel] || "other"
);

export const sampleEmails: CustomerEmail[] = entries.map(
  ([customerName, subject, body], index) => ({
    id: `EMAIL-${String(index + 1).padStart(3, "0")}`,
    customerName,
    customerEmail: `customer${index + 1}@example.com`,
    subject,
    body,
    receivedAt: new Date(
      Date.UTC(2026, 9, 1 + (index % 17), 9 + (index % 8), 0, 0)
    ).toISOString()
  })
);