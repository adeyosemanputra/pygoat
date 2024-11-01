
# Rapid Risk Assessment (RRA)
Purpose: This RRA template is designed to help assess the security impact of an application or service. 
Answer each question. Please contact <security team> if you have questions.

## Metadata

> Please update the service metadata

Service Name: 
Service Owner: 
Risk Impact Rating (if known):


## Threat Scenarios

### Confidentiality

> Please answer the following questions regarding confidentiality.

1. Would a breach of this service impact more than 10,000 users? (Yes/No)
2. Does this service handle or store medical data? (Yes/No)
3. Does this service handle or store financial data? (Yes/No)
4. Does this service handle or store credentials? (Yes/No)
5. Does this service handle or store sensitive personal information, such as Social Security Numbers, addresses, or phone numbers? (Yes/No)
6. Is this service subject to compliance certification (e.g. PCI, GDPR, HHIPAA)? (Yes/No)
7. Does this service involve the encryption, decryption, or key management of sensitive data? (Yes/No)
8. Does the service share sensitive data with any third-party systems or vendors? (Yes/No)
9. Does this service process or store intellectual property, proprietary algorithms, or confidential business information? (Yes/No)
10. Could a breach of this service allow unauthorized access to other critical systems or data stores? (Yes/No)
11. Does this service store or process data that, if disclosed, could harm the organization's brand reputation or customer trust? (Yes/No)

### Integrity

> Please answer the following questions to evaluate potential risks to data and process integrity.

1. Would a breach or compromise of this service impact the integrity of critical business functions such as financial reporting, customer data management, or regulatory compliance? (Yes/No)
2. Does this service handle account registration, password resets, or other processes essential to identity verification? (Yes/No)
3. Could a compromise of this service allow unauthorized modification of transactional data, financial records, or user data? (Yes/No)
4. Does this service integrate with any systems where tampering with data or transactions could have a significant financial or operational impact? (Yes/No)
5. Does this service rely on inputs from untrusted sources or third parties that could potentially compromise data integrity? (Yes/No)

### Availability

> Please answer the following questions to determine the importance of continuous access to this service.

1. Would an outage or downtime of this service impact more than 10,000 users? (Yes/No)
2. Would an outage of this service disrupt systems that are critical to critical business functions (e.g., customer transactions, order fulfillment, or emergency response)? (Yes/No)
3. Does this service have uptime or availability requirements due to regulatory, contractual, or customer SLAs (Service Level Agreements)? (Yes/No)
4. Would a failure of this service cascade to other dependent services or systems, impacting broader operational functions? (Yes/No)
5. Is this service deployed in a way that could make it more vulnerable to widespread availability issues, such as single points of failure or limited redundancy? (Yes/No)
