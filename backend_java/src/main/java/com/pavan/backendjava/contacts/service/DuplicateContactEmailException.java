package com.pavan.backendjava.contacts.service;

public class DuplicateContactEmailException extends RuntimeException {

    public DuplicateContactEmailException(String email) {
        super("A contact with email '%s' already exists".formatted(email));
    }
}
