import { z } from 'zod'

export const loanApplicationSchema = z.object({
    person_age: z.number()
        .min(18, 'Age must be at least 18')
        .max(120, 'Age must be less than 120')
        .or(z.string().transform(val => parseFloat(val))),

    person_income: z.number()
        .min(0, 'Income cannot be negative')
        .or(z.string().transform(val => parseFloat(val))),

    person_emp_length: z.number()
        .min(0, 'Employment length cannot be negative')
        .or(z.string().transform(val => parseFloat(val))),

    loan_amnt: z.number()
        .min(100, 'Loan amount must be at least 100')
        .or(z.string().transform(val => parseFloat(val))),

    loan_int_rate: z.number()
        .min(0, 'Interest rate cannot be negative')
        .max(100, 'Interest rate cannot exceed 100%')
        .or(z.string().transform(val => parseFloat(val))),

    loan_percent_income: z.number()
        .min(0, 'Percentage cannot be negative')
        .max(1, 'Percentage cannot exceed 1.0')
        .or(z.string().transform(val => parseFloat(val))),

    cb_person_cred_hist_length: z.number()
        .min(0, 'Credit history cannot be negative')
        .or(z.string().transform(val => parseFloat(val))),

    home_ownership: z.enum(['RENT', 'OWN', 'MORTGAGE', 'OTHER'], {
        errorMap: () => ({ message: 'Please select a valid home ownership status' })
    }),

    loan_intent: z.enum(['PERSONAL', 'EDUCATION', 'MEDICAL', 'VENTURE', 'HOMEIMPROVEMENT', 'DEBTCONSOLIDATION'], {
        errorMap: () => ({ message: 'Please select a valid loan purpose' })
    }),

    loan_grade: z.enum(['A', 'B', 'C', 'D', 'E', 'F', 'G'], {
        errorMap: () => ({ message: 'Please select a valid loan grade' })
    }),

    default_on_file: z.enum(['N', 'Y'], {
        errorMap: () => ({ message: 'Please select whether there is a default on file' })
    })
})
