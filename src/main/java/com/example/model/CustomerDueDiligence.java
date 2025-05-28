package com.example.model;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "customer_due_diligence")
public class CustomerDueDiligence {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "PROFILE_ID")
    private String profileId;

    @Column(name = "TENANT_ID")
    private String tenantId;

    @Column(name = "RISK_CATEGORY")
    private String riskCategory;  // HIGH, MEDIUM, LOW

    @Column(name = "KYC_STATUS")
    private String kycStatus;  // COMPLETE, PENDING, REVIEW_REQUIRED

    @Column(name = "LAST_REVIEW_DATE")
    private LocalDateTime lastReviewDate;

    @Column(name = "NEXT_REVIEW_DATE")
    private LocalDateTime nextReviewDate;

    @Column(name = "OCCUPATION")
    private String occupation;

    @Column(name = "INCOME_RANGE")
    private String incomeRange;  // 0-50K, 50K-100K, 100K-250K, 250K+

    @Column(name = "SOURCE_OF_FUNDS")
    private String sourceOfFunds;  // SALARY, BUSINESS, INVESTMENT, INHERITANCE

    @Column(name = "POLITICALLY_EXPOSED")
    private String politicallyExposed;  // Y, N

    @Column(name = "SANCTIONS_CHECK")
    private String sanctionsCheck;  // PASS, FAIL, REVIEW

    @Column(name = "MAKER_ID")
    private String makerId;

    @Column(name = "CHECKER_ID")
    private String checkerId;

    @Column(name = "MAKER_TIMESTAMP")
    private LocalDateTime makerTimestamp;

    @Column(name = "CHECKER_TIMESTAMP")
    private LocalDateTime checkerTimestamp;
} 