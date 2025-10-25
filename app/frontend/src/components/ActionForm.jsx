import { useState } from 'react';

export function ActionForm({
  id,
  title,
  description,
  fields,
  submitLabel,
  onSubmit,
  successLabel = 'Saved',
}) {
  const initialState = Object.fromEntries(
    fields.map((field) => [field.name, field.defaultValue ?? (field.kind === 'select' ? field.options?.[0]?.value ?? '' : '')])
  );
  const [state, setState] = useState(initialState);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    const nextValue = type === 'checkbox' ? checked : value;
    setState((current) => ({ ...current, [name]: nextValue }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await onSubmit(state);
      setStatus(successLabel);
      setState(initialState);
      setTimeout(() => setStatus(null), 2000);
    } catch (problem) {
      setError(problem.message || 'Unable to save');
    } finally {
      setBusy(false);
    }
  };

  return (
    <section id={id} className="card">
      <header className="card-header">
        <h3>{title}</h3>
        {description ? <p className="helper">{description}</p> : null}
      </header>
      <form className="stack" onSubmit={handleSubmit}>
        {fields.map((field) => {
          const common = {
            id: `${id}-${field.name}`,
            name: field.name,
            value: state[field.name] ?? '',
            onChange: handleChange,
            required: field.required,
            placeholder: field.placeholder,
          };
          return (
            <label key={field.name} className="form-field" htmlFor={`${id}-${field.name}`}>
              <span className="label">{field.label}</span>
              {field.kind === 'textarea' ? (
                <textarea {...common} rows={field.rows ?? 3} />
              ) : field.kind === 'select' ? (
                <select {...common}>
                  {field.options?.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              ) : (
                <input {...common} type={field.type ?? 'text'} />
              )}
            </label>
          );
        })}
        <div className="form-footer">
          <button type="submit" className="button primary" disabled={busy}>
            {busy ? 'Saving…' : submitLabel}
          </button>
          {status ? <span className="chip success">{status}</span> : null}
          {error ? <span className="chip danger">{error}</span> : null}
        </div>
      </form>
    </section>
  );
}
