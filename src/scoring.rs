//! Efficiency grading and XP.

use serde::{Deserialize, Serialize};

use crate::runner::trace::Steps;

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Grade {
    Bronze,
    Silver,
    Gold,
}

impl Grade {
    pub fn multiplier(self) -> f64 {
        match self {
            Grade::Gold => 1.5,
            Grade::Silver => 1.2,
            Grade::Bronze => 1.0,
        }
    }

    pub fn letter(self) -> &'static str {
        match self {
            Grade::Gold => "A",
            Grade::Silver => "B",
            Grade::Bronze => "C",
        }
    }

    pub fn medal(self) -> &'static str {
        match self {
            Grade::Gold => "GOLD",
            Grade::Silver => "SILVER",
            Grade::Bronze => "BRONZE",
        }
    }
}

#[derive(Debug, Clone, PartialEq)]
pub struct Report {
    pub grade: Grade,
    pub user_slope: f64,
    pub ref_slope: f64,
    /// User steps divided by reference steps at the largest measured size.
    pub ratio: f64,
    pub user_steps: u64,
    pub ref_steps: u64,
    pub n: u32,
}

/// Least-squares slope of ln(steps) against ln(n): the empirical growth exponent.
pub fn slope(points: &[(u32, u64)]) -> f64 {
    let pts: Vec<(f64, f64)> =
        points.iter().filter(|(n, s)| *n > 0 && *s > 0).map(|(n, s)| (f64::from(*n).ln(), (*s as f64).ln())).collect();
    if pts.len() < 2 {
        return 0.0;
    }
    let k = pts.len() as f64;
    let mx = pts.iter().map(|p| p.0).sum::<f64>() / k;
    let my = pts.iter().map(|p| p.1).sum::<f64>() / k;
    let num: f64 = pts.iter().map(|p| (p.0 - mx) * (p.1 - my)).sum();
    let den: f64 = pts.iter().map(|p| (p.0 - mx).powi(2)).sum();
    if den == 0.0 { 0.0 } else { num / den }
}

/// Same growth class when the user's exponent is within this margin of the reference's.
const CLASS_MARGIN: f64 = 0.3;

pub fn grade(steps: &Steps, limit_hit: bool) -> Report {
    let user_slope = slope(&steps.user);
    let ref_slope = slope(&steps.reference);
    let (n, user_steps) = steps.user.last().copied().unwrap_or((0, 0));
    let ref_steps = steps.reference.iter().find(|(rn, _)| *rn == n).map_or(0, |(_, s)| *s);
    let ratio = if ref_steps == 0 { 1.0 } else { user_steps as f64 / ref_steps as f64 };
    let same_class = !limit_hit && user_slope <= ref_slope + CLASS_MARGIN;
    let grade = if same_class && ratio <= 1.25 {
        Grade::Gold
    } else if same_class && ratio <= 2.5 {
        Grade::Silver
    } else {
        Grade::Bronze
    };
    Report { grade, user_slope, ref_slope, ratio, user_steps, ref_steps, n }
}

/// Describe an empirical exponent the way people talk about growth.
pub fn growth_name(exp: f64) -> &'static str {
    match exp {
        e if e < 0.35 => "~O(log n) or better",
        e if e < 1.12 => "~O(n)",
        e if e < 1.45 => "~O(n log n)",
        e if e < 2.4 => "~O(n^2)",
        e if e < 3.4 => "~O(n^3)",
        _ => "steep",
    }
}

/// XP earned for a submission, before subtracting what was already awarded.
pub fn award(base: u32, grade: Option<Grade>, hints_used: u32) -> u32 {
    let mult = grade.map_or(1.0, Grade::multiplier);
    let hint_factor = 1.0 - 0.1 * f64::from(hints_used.min(3));
    (f64::from(base) * mult * hint_factor).round() as u32
}

/// Level for a total XP: level L needs 50 * L * (L + 1) XP.
pub fn level(xp: u64) -> u32 {
    let mut l = 0u32;
    while xp >= level_floor(l + 1) {
        l += 1;
    }
    l
}

pub fn level_floor(l: u32) -> u64 {
    50 * u64::from(l) * (u64::from(l) + 1)
}

/// Progress through the current level, 0.0..1.0.
pub fn level_progress(xp: u64) -> f64 {
    let l = level(xp);
    let lo = level_floor(l);
    let hi = level_floor(l + 1);
    (xp - lo) as f64 / (hi - lo) as f64
}

#[cfg(test)]
mod tests {
    use super::*;

    fn curve(f: impl Fn(f64) -> f64) -> Vec<(u32, u64)> {
        [64u32, 128, 256, 512].iter().map(|&n| (n, f(f64::from(n)).round() as u64)).collect()
    }

    #[test]
    fn slope_recovers_exponents() {
        assert!((slope(&curve(|n| 3.0 * n)) - 1.0).abs() < 0.01);
        assert!((slope(&curve(|n| n * n / 2.0)) - 2.0).abs() < 0.01);
        let nlogn = slope(&curve(|n| n * n.log2()));
        assert!(nlogn > 1.1 && nlogn < 1.3, "{nlogn}");
        assert!(slope(&curve(|n| 5.0 * n.log2())) < 0.35);
    }

    #[test]
    fn grades_follow_class_and_ratio() {
        let reference = curve(|n| 4.0 * n);
        let g = |user: Vec<(u32, u64)>| grade(&Steps { user, reference: reference.clone() }, false).grade;
        assert_eq!(g(curve(|n| 4.4 * n)), Grade::Gold);
        assert_eq!(g(curve(|n| 2.0 * n)), Grade::Gold);
        assert_eq!(g(curve(|n| 8.0 * n)), Grade::Silver);
        assert_eq!(g(curve(|n| 20.0 * n)), Grade::Bronze);
        assert_eq!(g(curve(|n| n * n)), Grade::Bronze);
        let limited = grade(&Steps { user: curve(|n| 4.0 * n), reference: reference.clone() }, true);
        assert_eq!(limited.grade, Grade::Bronze);
    }

    #[test]
    fn xp_and_levels() {
        assert_eq!(award(100, Some(Grade::Gold), 0), 150);
        assert_eq!(award(100, Some(Grade::Bronze), 2), 80);
        assert_eq!(award(100, None, 9), 70);
        assert_eq!(level(0), 0);
        assert_eq!(level(99), 0);
        assert_eq!(level(100), 1);
        assert_eq!(level(300), 2);
        assert!((level_progress(200) - 0.5).abs() < 1e-9);
    }
}
