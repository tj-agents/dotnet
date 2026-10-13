namespace Shared;

public interface IError
{
    ErrorDefinition Definition { get; }
}

public sealed class ErrorDefinition
{
    public required string Code { get; init; }
    public required string Message { get; init; }

    public static ErrorDefinition Invalid<TCase>() => Create<TCase>("invalid", "");
    public static ErrorDefinition Invalid<TCase>(string message) => Create<TCase>("invalid", message);
    public static ErrorDefinition NotFound<TCase>() => Create<TCase>("not_found", "");
    public static ErrorDefinition NotFound<TCase>(string message) => Create<TCase>("not_found", message);
    public static ErrorDefinition Conflict<TCase>() => Create<TCase>("conflict", "");
    public static ErrorDefinition Conflict<TCase>(string message) => Create<TCase>("conflict", message);
    public static ErrorDefinition Unauthenticated<TCase>() => Create<TCase>("unauthenticated", "");
    public static ErrorDefinition Unauthenticated<TCase>(string message) => Create<TCase>("unauthenticated", message);
    public static ErrorDefinition Forbidden<TCase>() => Create<TCase>("forbidden", "");
    public static ErrorDefinition Forbidden<TCase>(string message) => Create<TCase>("forbidden", message);
    public static ErrorDefinition PaymentRequired<TCase>() => Create<TCase>("payment_required", "");
    public static ErrorDefinition PaymentRequired<TCase>(string message) => Create<TCase>("payment_required", message);
    public static ErrorDefinition Validation<TCase>(ValidationErrors errors) => Create<TCase>("validation", "Validation failed.");

    private static ErrorDefinition Create<TCase>(string code, string message) =>
        new() { Code = $"{typeof(TCase).Name}.{code}", Message = message };
}

public sealed class ValidationErrors
{
    public ValidationErrors(IReadOnlyDictionary<string, IReadOnlyList<string>> fields) => Fields = fields;

    public IReadOnlyDictionary<string, IReadOnlyList<string>> Fields { get; }
}

public sealed class ValidationResult
{
    private readonly ValidationErrors? errors;

    private ValidationResult(ValidationErrors? errors) => this.errors = errors;

    public static ValidationResult Valid { get; } = new(null);

    public bool IsValid => errors is null;

    public static ValidationResult Invalid(ValidationErrors errors) => new(errors);

    public static implicit operator UnitResult<ValidationErrors>(ValidationResult result) =>
        result.errors is null ? new Success() : new Failure<ValidationErrors>(result.errors);

    public bool TryGetErrors(out ValidationErrors value)
    {
        value = errors!;
        return errors is not null;
    }
}

public static class ValidationResultExtensions
{
    public static ValidationResult Combine(this IEnumerable<ValidationResult> results)
    {
        var failed = results.Where(result => !result.IsValid).ToList();
        if (failed.Count == 0)
            return ValidationResult.Valid;
        failed[0].TryGetErrors(out var errors);
        return ValidationResult.Invalid(errors);
    }
}

public readonly struct Success
{
}

public readonly struct Success<T>
{
    public Success(T value) => Value = value;

    public T Value { get; }
}

public readonly struct Failure<TError>
{
    public Failure(TError error) => Error = error;

    public TError Error { get; }
}

public readonly struct Option<T>
{
    private readonly T? value;
    private readonly bool hasValue;

    private Option(T? value, bool hasValue)
    {
        this.value = value;
        this.hasValue = hasValue;
    }

    public static implicit operator Option<T>(T? value) => new(value, value is not null);

    public TResult Match<TResult>(Func<T, TResult> onSome, Func<TResult> onNone) =>
        hasValue ? onSome(value!) : onNone();

    public bool TryGetValue(out T value)
    {
        value = this.value!;
        return hasValue;
    }

    public T ValueOr(T fallback) => hasValue ? value! : fallback;
}

public static class OptionTaskExtensions
{
    public static async Task<T> ValueOr<T>(this Task<Option<T>> task, T fallback) =>
        (await task.ConfigureAwait(false)).ValueOr(fallback);

    public static async Task<Result<T, TError>> OrFailure<T, TError>(this Task<Option<T>> task, TError error)
    {
        var option = await task.ConfigureAwait(false);
        return option.TryGetValue(out var value) ? new Success<T>(value) : new Failure<TError>(error);
    }
}

public readonly struct Result<TValue, TError>
{
    private readonly TValue? value;
    private readonly TError? error;
    private readonly bool isSuccess;

    private Result(TValue? value, TError? error, bool isSuccess)
    {
        this.value = value;
        this.error = error;
        this.isSuccess = isSuccess;
    }

    public static implicit operator Result<TValue, TError>(TValue value) => new(value, default, true);
    public static implicit operator Result<TValue, TError>(TError error) => new(default, error, false);
    public static implicit operator Result<TValue, TError>(Success<TValue> success) => new(success.Value, default, true);
    public static implicit operator Result<TValue, TError>(Failure<TError> failure) => new(default, failure.Error, false);

    public bool TryGetValue(out TValue value)
    {
        value = this.value!;
        return isSuccess;
    }

    public bool TryGetError(out TError error)
    {
        error = this.error!;
        return !isSuccess;
    }

    public TResult Match<TResult>(Func<TValue, TResult> onSuccess, Func<TError, TResult> onFailure) =>
        isSuccess ? onSuccess(value!) : onFailure(error!);

    public Result<TValue, TError> Ensure(
        Func<TValue, ValidationResult> predicate, Func<ValidationErrors, TError> onInvalid)
    {
        if (!isSuccess)
            return this;
        var validation = predicate(value!);
        return validation.TryGetErrors(out var errors) ? new Failure<TError>(onInvalid(errors)) : this;
    }
}

public static class ResultTaskExtensions
{
    public static async Task<Result<TValue, TError>> Ensure<TValue, TError>(
        this Task<Result<TValue, TError>> task,
        Func<TValue, ValidationResult> predicate,
        Func<ValidationErrors, TError> onInvalid) =>
        (await task.ConfigureAwait(false)).Ensure(predicate, onInvalid);

    public static async Task<Result<TNext, TError>> MapAsync<TValue, TError, TNext>(
        this Task<Result<TValue, TError>> task, Func<TValue, Task<TNext>> mapper)
    {
        var result = await task.ConfigureAwait(false);
        return result.TryGetValue(out var value)
            ? new Success<TNext>(await mapper(value).ConfigureAwait(false))
            : new Failure<TError>(result.TryGetError(out var error) ? error : default!);
    }
}

public readonly struct UnitResult<TError>
{
    private readonly TError? error;
    private readonly bool isSuccess;

    private UnitResult(TError? error, bool isSuccess)
    {
        this.error = error;
        this.isSuccess = isSuccess;
    }

    public static implicit operator UnitResult<TError>(Success success) => new(default, true);
    public static implicit operator UnitResult<TError>(TError error) => new(error, false);
    public static implicit operator UnitResult<TError>(Failure<TError> failure) => new(failure.Error, false);
}
