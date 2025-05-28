package com.example.model;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;
import java.util.List;

@Data
@Entity
@Table(name = "customer_address")
public class CustomerAddress {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "PROFILE_ID")
    private String profileId;

    @Column(name = "TENANT_ID")
    private String tenantId;

    @Column(name = "ADDRESS_TYPE")
    private String addressType;  // RES, OFF, PER, ALT, MAI

    @Column(name = "ADDRESS_1")
    private String address1;

    @Column(name = "ADDRESS_2")
    private String address2;

    @Column(name = "ADDRESS_3")
    private String address3;

    @Column(name = "NEAREST_LANDMARK")
    private String nearestLandmark;

    @Column(name = "CITY_NAME")
    private String cityName;

    @Column(name = "STATE_NAME")
    private String stateName;

    @Column(name = "COUNTRY_CODE")
    private String countryCode;

    @Column(name = "POSTAL_CODE")
    private String postalCode;

    @Column(name = "WAU_FLAG")
    private String wauFlag;  // Y, N

    @Column(name = "MAIL_ADDR_IND")
    private String mailAddrInd;  // Y

    @Column(name = "ADDRESS_CLASSIFICATION")
    private String addressClassification;

    @Column(name = "POST_BOX_NO")
    private String postBoxNo;

    @Column(name = "RMAIL_COUNTER")
    private String rmailCounter;

    @Column(name = "RESET_RMAIL_FLAG")
    private String resetRmailFlag;  // Y, N

    @Column(name = "MAKER_ID")
    private String makerId;

    @Column(name = "CHECKER_ID")
    private String checkerId;

    @Column(name = "MAKER_TIMESTAMP")
    private LocalDateTime makerTimestamp;

    @Column(name = "CHECKER_TIMESTAMP")
    private LocalDateTime checkerTimestamp;

    @Column(name = "POA_DOCUMENT")
    private String poaDocument;

    @Column(name = "STATE_CODE")
    private String stateCode;

    @Column(name = "SYSTEM_LAST_AMENDED")
    private String systemLastAmended;

    @Column(name = "USER_LAST_AMENDED")
    private String userLastAmended;

    @Column(name = "SYSTEM_ID")
    private String systemId;

//    @OneToMany(cascade = CascadeType.ALL)
//    @JoinColumn(name = "ADDRESS_ID")
//    private List<CustomerAddressException> addressExceptions;
} 