package org.example.week2.dto;

import lombok.Data;

@Data
public class UserPatchRequest {

    private String username;

    private String email;

}