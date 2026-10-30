//! System design quizzes: answer parsing, checking and grading.

use crate::content::Question;
use crate::scoring::Grade;

/// Wrong attempts allowed before the answer is revealed.
pub const MAX_ATTEMPTS: u8 = 2;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Answer {
    /// 0-based index of the selected choice.
    Choice(usize),
    Number(f64),
}

/// Parse a number the way people write estimates: `12000`, `12,000`, `12k`, `1.2M`, `3e6`, `2.5GB`, `99.9%`.
pub fn parse_number(input: &str) -> Option<f64> {
    let cleaned: String =
        input.trim().chars().filter(|c| !matches!(c, ',' | '_' | ' ')).collect::<String>().to_lowercase();
    if cleaned.is_empty() {
        return None;
    }
    if let Ok(v) = cleaned.trim_end_matches('%').parse::<f64>() {
        return v.is_finite().then_some(v);
    }
    // a trailing byte unit carries no scale of its own: "2.5gb" is 2.5 with the g suffix
    let body = cleaned.strip_suffix('b').filter(|b| b.ends_with(['k', 'm', 'g', 't'])).unwrap_or(&cleaned);
    let (digits, scale) = match body.chars().last()? {
        'k' => (&body[..body.len() - 1], 1e3),
        'm' => (&body[..body.len() - 1], 1e6),
        'b' | 'g' => (&body[..body.len() - 1], 1e9),
        't' => (&body[..body.len() - 1], 1e12),
        _ => return None,
    };
    let v = digits.parse::<f64>().ok()? * scale;
    v.is_finite().then_some(v)
}

/// Whether an answer is accepted for a question.
pub fn is_correct(q: &Question, answer: Answer) -> bool {
    match answer {
        Answer::Choice(i) => q.is_answer(i),
        Answer::Number(x) => {
            if q.answer == 0.0 {
                x.abs() <= q.tolerance
            } else {
                ((x - q.answer) / q.answer).abs() <= q.tolerance
            }
        }
    }
}

/// Grade a finished quiz by how many questions were right on the first try.
pub fn grade(first_try: usize, total: usize) -> Grade {
    if total == 0 || first_try == total {
        Grade::Gold
    } else if first_try * 5 >= total * 3 {
        Grade::Silver
    } else {
        Grade::Bronze
    }
}

/// A number in the compact form used for answers: 11,574 or 2.5M.
pub fn format_number(v: f64) -> String {
    let abs = v.abs();
    let (scaled, suffix) = match abs {
        a if a >= 1e12 => (v / 1e12, "T"),
        a if a >= 1e9 => (v / 1e9, "B"),
        a if a >= 1e7 => (v / 1e6, "M"),
        _ => (v, ""),
    };
    if suffix.is_empty() {
        if v.fract() == 0.0 {
            let digits = format!("{}", v.abs() as u64);
            let mut out = String::new();
            for (i, c) in digits.chars().enumerate() {
                if i > 0 && (digits.len() - i).is_multiple_of(3) {
                    out.push(',');
                }
                out.push(c);
            }
            return if v < 0.0 { format!("-{out}") } else { out };
        }
        return format!("{v:.3}").trim_end_matches('0').trim_end_matches('.').to_string();
    }
    format!("{}{suffix}", format!("{scaled:.2}").trim_end_matches('0').trim_end_matches('.'))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn number_question(answer: f64, tolerance: f64) -> Question {
        Question {
            prompt: String::new(),
            choices: Vec::new(),
            answer,
            tolerance,
            unit: String::new(),
            hint: String::new(),
            explanation: String::new(),
            steps: Vec::new(),
        }
    }

    #[test]
    fn parses_estimate_notation() {
        assert_eq!(parse_number("12000"), Some(12000.0));
        assert_eq!(parse_number(" 12,000 "), Some(12000.0));
        assert_eq!(parse_number("12k"), Some(12000.0));
        assert_eq!(parse_number("1.2M"), Some(1_200_000.0));
        assert_eq!(parse_number("3e6"), Some(3_000_000.0));
        assert_eq!(parse_number("2.5GB"), Some(2.5e9));
        assert_eq!(parse_number("4TB"), Some(4e12));
        assert_eq!(parse_number("2b"), Some(2e9));
        assert_eq!(parse_number("99.9%"), Some(99.9));
        assert_eq!(parse_number("1_000"), Some(1000.0));
        assert_eq!(parse_number(""), None);
        assert_eq!(parse_number("lots"), None);
        assert_eq!(parse_number("k"), None);
    }

    #[test]
    fn number_answers_accept_relative_tolerance() {
        let q = number_question(11_574.0, 0.25);
        assert!(is_correct(&q, Answer::Number(12_000.0)));
        assert!(is_correct(&q, Answer::Number(9_000.0)));
        assert!(!is_correct(&q, Answer::Number(8_000.0)));
        assert!(!is_correct(&q, Answer::Choice(0)));
        let zero = number_question(0.0, 0.01);
        assert!(is_correct(&zero, Answer::Number(0.0)));
    }

    #[test]
    fn choice_answers_are_one_based() {
        let mut q = number_question(2.0, 0.25);
        q.choices = vec!["a".into(), "b".into(), "c".into()];
        assert!(is_correct(&q, Answer::Choice(1)));
        assert!(!is_correct(&q, Answer::Choice(0)));
    }

    #[test]
    fn grades_by_first_try_accuracy() {
        assert_eq!(grade(4, 4), Grade::Gold);
        assert_eq!(grade(3, 4), Grade::Silver);
        assert_eq!(grade(3, 5), Grade::Silver);
        assert_eq!(grade(2, 5), Grade::Bronze);
    }

    #[test]
    fn formats_answers_compactly() {
        assert_eq!(format_number(11_574.0), "11,574");
        assert_eq!(format_number(2_500_000_000.0), "2.5B");
        assert_eq!(format_number(12_000_000.0), "12M");
        assert_eq!(format_number(0.5), "0.5");
        assert_eq!(format_number(99.95), "99.95");
    }
}
