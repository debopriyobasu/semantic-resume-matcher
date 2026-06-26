// Configuration schema for form fields on resume upload page
export const RESUME_UPLOAD_FIELDS = [
  {
    name: 'desired_salary',
    label: 'Desired Salary (Annual $)',
    type: 'number',
    placeholder: 'e.g. 120000',
    helpText: 'Hard boundary filter against job maximum salary bounds.'
  },
  {
    name: 'visa_required',
    label: 'Requires Visa Sponsorship',
    type: 'toggle',
    defaultValue: false,
    helpText: 'Reject jobs that do not support visa sponsorship.'
  },
  {
    name: 'preferred_location',
    label: 'Preferred Location (City, State)',
    type: 'text',
    placeholder: 'e.g. San Francisco, CA',
    helpText: 'Deterministic match on exact job location string.'
  },
  {
    name: 'preferred_remote',
    label: 'Remote Only Preference',
    type: 'toggle',
    defaultValue: false,
    helpText: 'Filter out jobs that do not allow remote work.'
  }
];
