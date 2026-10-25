package com.pavan.backendjava.contacts.service;

public class ContactNotFoundException extends RuntimeException {

    public ContactNotFoundException(String id) {
        super("Contact '%s' was not found".formatted(id));
    }
}
