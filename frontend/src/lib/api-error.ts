export class ApiError extends Error {
  constructor(
    message: string,
    public response: {
      data: unknown;
      status: number;
    }
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
