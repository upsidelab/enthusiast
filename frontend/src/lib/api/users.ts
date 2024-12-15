import { BaseApiClient } from "@/lib/api/base.ts";
import { PaginatedResult, User } from "@/lib/types.ts";

export type CreateUserParams = {
  email: string;
  password: string;
  isStaff: boolean;
  isActive: boolean;
}

export type UpdateUserParams = {
  email: string;
  isStaff: boolean;
  isActive: boolean;
}

export type CreateUserPayload = {
  email: string;
  password: string;
  is_staff: boolean;
  is_active: boolean;
}

export type UpdateUserPayload = {
  email: string;
  is_staff: boolean;
  is_active: boolean;
}

export type UpdateUserPasswordPayload = {
  password: string;
}

export type UserResponse = {
  id: number;
  email: string;
  is_staff: boolean;
  is_active: boolean;
}

export class UsersApiClient extends BaseApiClient {
  async getUsers(page: number): Promise<PaginatedResult<User>> {
    const response = await fetch(`${this.apiBase}/api/users?page=${page}`, this._requestConfiguration());
    const result = await response.json() as PaginatedResult<UserResponse>;

    return {
      count: result.count,
      results: result.results.map((item) => ({
        id: item.id,
        email: item.email,
        isStaff: item.is_staff,
        isActive: item.is_active
      }))
    };
  }

  async createUser(user: CreateUserParams) {
    const payload: CreateUserPayload = {
      email: user.email,
      password: user.password,
      is_staff: user.isStaff,
      is_active: user.isActive
    };

    return await fetch(
      `${this.apiBase}/api/users`,
      {
        ...this._requestConfiguration(),
        method: "POST",
        body: JSON.stringify(payload)
      }
    );
  }

  async updateUser(userId: number, user: UpdateUserParams) {
    const payload: UpdateUserPayload = {
      email: user.email,
      is_staff: user.isStaff,
      is_active: user.isActive
    };

    return await fetch(
      `${this.apiBase}/api/users/${userId}`,
      {
        ...this._requestConfiguration(),
        method: "PATCH",
        body: JSON.stringify(payload)
      }
    );
  }

  async updateUserPassword(userId: number, password: string) {
    const payload: UpdateUserPasswordPayload = {
      password: password
    };

    return await fetch(
      `${this.apiBase}/api/users/${userId}/password`,
      {
        ...this._requestConfiguration(),
        method: "PUT",
        body: JSON.stringify(payload)
      }
    )
  }
}
