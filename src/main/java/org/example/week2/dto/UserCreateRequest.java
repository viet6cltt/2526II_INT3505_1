package org.example.week2.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class UserCreateRequest {
    @NotBlank(message = "username is required")
    private String username;

    @NotBlank(message = "email is required")
    private String email;

}