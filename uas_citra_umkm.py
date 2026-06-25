import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class AplikasiPengolahanCitra:
    def __init__(self, window):
        self.window = window
        self.window.title("Aplikasi Pengolahan Citra Digital - Produk UMKM")
        self.window.geometry("1200x700")
        self.window.configure(bg="#2c3e50")

        self.path_gambar = None
        self.gambar_asli = None
        self.gambar_proses = None
        self.nama_proses = tk.StringVar(value="Belum ada proses dipilih")

        # ===================== PANEL KIRI (MENU) =====================
        self.panel_tombol = tk.Frame(window, width=230, bg="#34495e", relief=tk.FLAT)
        self.panel_tombol.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        self.panel_tombol.pack_propagate(False)

        # Judul Aplikasi
        tk.Label(
            self.panel_tombol,
            text="🖼 Pengolahan\nCitra Digital",
            font=("Arial", 13, "bold"),
            bg="#34495e", fg="white"
        ).pack(pady=(15, 5))

        tk.Label(self.panel_tombol, text="Produk UMKM", font=("Arial", 9), bg="#34495e", fg="#95a5a6").pack()
        tk.Frame(self.panel_tombol, height=1, bg="#5d6d7e").pack(fill=tk.X, padx=10, pady=10)

        # Tombol Pilih Gambar
        tk.Button(
            self.panel_tombol, text="📂  Pilih Gambar UMKM",
            command=self.pilih_gambar, width=24,
            bg="#27ae60", fg="white", font=("Arial", 9, "bold"),
            relief=tk.FLAT, cursor="hand2", pady=6
        ).pack(pady=(5, 10), padx=10)

        # --- 1. Konversi Citra ---
        self._buat_label_seksi("1. Konversi Citra")
        tk.Button(self.panel_tombol, text="RGB → Grayscale", command=self.proses_grayscale, **self._style_btn()).pack(pady=2, padx=10, fill=tk.X)
        tk.Button(self.panel_tombol, text="RGB → Biner (Otsu)", command=self.proses_biner, **self._style_btn()).pack(pady=2, padx=10, fill=tk.X)

        # --- 2. Perbaikan Kualitas ---
        self._buat_label_seksi("2. Perbaikan Kualitas")
        tk.Button(self.panel_tombol, text="Histogram Equalization", command=self.proses_equalization, **self._style_btn()).pack(pady=2, padx=10, fill=tk.X)
        tk.Button(self.panel_tombol, text="Contrast Stretching", command=self.proses_contrast_stretching, **self._style_btn()).pack(pady=2, padx=10, fill=tk.X)

        # --- 3. Filtering ---
        self._buat_label_seksi("3. Filtering")
        tk.Button(self.panel_tombol, text="Mean Filter", command=self.proses_mean, **self._style_btn()).pack(pady=2, padx=10, fill=tk.X)
        tk.Button(self.panel_tombol, text="Median Filter", command=self.proses_median, **self._style_btn()).pack(pady=2, padx=10, fill=tk.X)
        tk.Button(self.panel_tombol, text="Gaussian Filter", command=self.proses_gaussian, **self._style_btn()).pack(pady=2, padx=10, fill=tk.X)

        # --- 4. Deteksi Tepi ---
        self._buat_label_seksi("4. Deteksi Tepi")
        tk.Button(self.panel_tombol, text="Sobel Edge Detection", command=self.proses_sobel, **self._style_btn()).pack(pady=2, padx=10, fill=tk.X)
        tk.Button(self.panel_tombol, text="Canny Edge Detection", command=self.proses_canny, **self._style_btn()).pack(pady=2, padx=10, fill=tk.X)

        # --- 5. Segmentasi ---
        self._buat_label_seksi("5. Segmentasi Citra")
        tk.Button(self.panel_tombol, text="Threshold Segmentation", command=self.proses_threshold, **self._style_btn()).pack(pady=2, padx=10, fill=tk.X)
        tk.Button(self.panel_tombol, text="K-Means Segmentation", command=self.proses_kmeans, **self._style_btn()).pack(pady=2, padx=10, fill=tk.X)

        tk.Frame(self.panel_tombol, height=1, bg="#5d6d7e").pack(fill=tk.X, padx=10, pady=10)

        # Tombol Simpan Hasil
        tk.Button(
            self.panel_tombol, text="💾  Simpan Hasil",
            command=self.simpan_gambar, width=24,
            bg="#2980b9", fg="white", font=("Arial", 9, "bold"),
            relief=tk.FLAT, cursor="hand2", pady=6
        ).pack(pady=5, padx=10)

        # ===================== PANEL KANAN (TAMPILAN) =====================
        self.panel_kanan = tk.Frame(window, bg="#2c3e50")
        self.panel_kanan.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)

        # Label nama proses aktif
        tk.Label(
            self.panel_kanan,
            textvariable=self.nama_proses,
            font=("Arial", 10, "italic"),
            bg="#2c3e50", fg="#f39c12"
        ).pack(pady=(0, 5))

        # Frame gambar
        self.panel_gambar = tk.Frame(self.panel_kanan, bg="#2c3e50")
        self.panel_gambar.pack(fill=tk.BOTH, expand=True)

        self.panel_gambar.grid_columnconfigure(0, weight=1)
        self.panel_gambar.grid_columnconfigure(1, weight=1)
        self.panel_gambar.grid_rowconfigure(1, weight=1)

        # Header kolom
        tk.Label(self.panel_gambar, text="GAMBAR ASLI", font=("Arial", 10, "bold"), bg="#2c3e50", fg="#ecf0f1").grid(row=0, column=0, pady=(0, 5))
        tk.Label(self.panel_gambar, text="GAMBAR HASIL PROSES", font=("Arial", 10, "bold"), bg="#2c3e50", fg="#ecf0f1").grid(row=0, column=1, pady=(0, 5))

        # Canvas gambar asli
        self.lbl_canvas_asli = tk.Label(
            self.panel_gambar,
            text="Gambar Asli\n(Belum Dimuat)",
            bg="#1a252f", fg="#7f8c8d",
            font=("Arial", 10), relief=tk.FLAT, bd=0
        )
        self.lbl_canvas_asli.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # Canvas gambar hasil
        self.lbl_canvas_hasil = tk.Label(
            self.panel_gambar,
            text="Gambar Hasil\n(Pilih proses di kiri)",
            bg="#1a252f", fg="#7f8c8d",
            font=("Arial", 10), relief=tk.FLAT, bd=0
        )
        self.lbl_canvas_hasil.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

        # Status bar bawah
        self.status_var = tk.StringVar(value="Selamat datang! Pilih gambar untuk memulai.")
        tk.Label(
            self.panel_kanan,
            textvariable=self.status_var,
            font=("Arial", 9), bg="#1a252f", fg="#95a5a6",
            anchor="w", padx=10, pady=4
        ).pack(fill=tk.X, pady=(5, 0))

    # ===================== HELPER UI =====================
    def _style_btn(self):
        return dict(bg="#4a6278", fg="white", font=("Arial", 9), relief=tk.FLAT, cursor="hand2", pady=4, activebackground="#5d7a95")

    def _buat_label_seksi(self, teks):
        tk.Label(self.panel_tombol, text=teks, font=("Arial", 9, "bold"), bg="#2c3e50", fg="#f39c12", anchor="w").pack(fill=tk.X, padx=10, pady=(8, 2))

    # ===================== FUNGSI UTAMA =====================
    def pilih_gambar(self):
        self.path_gambar = filedialog.askopenfilename(
            title="Pilih Gambar Produk UMKM",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if self.path_gambar:
            self.gambar_asli = cv2.imread(self.path_gambar)
            self.tampilkan_gambar(self.gambar_asli, target="asli")
            nama_file = os.path.basename(self.path_gambar)
            self.status_var.set(f"Gambar dimuat: {nama_file}")
            self.nama_proses.set("Gambar berhasil dimuat. Pilih proses di sebelah kiri.")
            # Reset hasil
            self.lbl_canvas_hasil.config(image="", text="Gambar Hasil\n(Pilih proses di kiri)", bg="#1a252f")
            self.lbl_canvas_hasil.image = None

    def tampilkan_gambar(self, img_cv, target="hasil"):
        if img_cv is None:
            return
        if len(img_cv.shape) == 3:
            img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_GRAY2RGB)

        img_pil = Image.fromarray(img_rgb)
        img_pil = img_pil.resize((420, 420), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_pil)

        if target == "asli":
            self.lbl_canvas_asli.config(image=img_tk, text="", bg="#1a252f")
            self.lbl_canvas_asli.image = img_tk
        else:
            self.lbl_canvas_hasil.config(image=img_tk, text="", bg="#1a252f")
            self.lbl_canvas_hasil.image = img_tk

    def _cek_gambar(self):
        if self.gambar_asli is None:
            messagebox.showwarning("Peringatan", "Silakan pilih gambar terlebih dahulu!")
            return False
        return True

    def simpan_gambar(self):
        if self.gambar_proses is None:
            messagebox.showwarning("Peringatan", "Belum ada hasil proses untuk disimpan!")
            return
        path_simpan = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")]
        )
        if path_simpan:
            cv2.imwrite(path_simpan, self.gambar_proses if len(self.gambar_proses.shape) == 3
                        else self.gambar_proses)
            messagebox.showinfo("Berhasil", f"Gambar berhasil disimpan:\n{path_simpan}")
            self.status_var.set(f"Gambar disimpan: {os.path.basename(path_simpan)}")

    # ===================== 1. KONVERSI CITRA =====================
    def proses_grayscale(self):
        if not self._cek_gambar(): return
        self.gambar_proses = cv2.cvtColor(self.gambar_asli, cv2.COLOR_BGR2GRAY)
        self.tampilkan_gambar(self.gambar_proses)
        self.nama_proses.set("Proses: RGB → Grayscale")
        self.status_var.set("Konversi RGB ke Grayscale selesai.")

    def proses_biner(self):
        if not self._cek_gambar(): return
        gray = cv2.cvtColor(self.gambar_asli, cv2.COLOR_BGR2GRAY)
        _, self.gambar_proses = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        self.tampilkan_gambar(self.gambar_proses)
        self.nama_proses.set("Proses: RGB → Biner (Otsu Thresholding)")
        self.status_var.set("Konversi RGB ke Biner (Otsu) selesai.")

    # ===================== 2. PERBAIKAN KUALITAS =====================
    def proses_equalization(self):
        if not self._cek_gambar(): return
        gray = cv2.cvtColor(self.gambar_asli, cv2.COLOR_BGR2GRAY)
        self.gambar_proses = cv2.equalizeHist(gray)
        self.tampilkan_gambar(self.gambar_proses)
        self.nama_proses.set("Proses: Histogram Equalization")
        self.status_var.set("Histogram Equalization selesai.")

    def proses_contrast_stretching(self):
        if not self._cek_gambar(): return
        gray = cv2.cvtColor(self.gambar_asli, cv2.COLOR_BGR2GRAY)
        p_min = np.percentile(gray, 2)
        p_max = np.percentile(gray, 98)
        stretched = np.clip((gray - p_min) * 255.0 / (p_max - p_min), 0, 255).astype(np.uint8)
        self.gambar_proses = stretched
        self.tampilkan_gambar(self.gambar_proses)
        self.nama_proses.set("Proses: Contrast Stretching")
        self.status_var.set("Contrast Stretching selesai.")

    # ===================== 3. FILTERING =====================
    def proses_mean(self):
        if not self._cek_gambar(): return
        self.gambar_proses = cv2.blur(self.gambar_asli, (5, 5))
        self.tampilkan_gambar(self.gambar_proses)
        self.nama_proses.set("Proses: Mean Filter (kernel 5x5)")
        self.status_var.set("Mean Filter selesai.")

    def proses_median(self):
        if not self._cek_gambar(): return
        self.gambar_proses = cv2.medianBlur(self.gambar_asli, 5)
        self.tampilkan_gambar(self.gambar_proses)
        self.nama_proses.set("Proses: Median Filter (kernel 5x5)")
        self.status_var.set("Median Filter selesai.")

    def proses_gaussian(self):
        if not self._cek_gambar(): return
        self.gambar_proses = cv2.GaussianBlur(self.gambar_asli, (5, 5), 0)
        self.tampilkan_gambar(self.gambar_proses)
        self.nama_proses.set("Proses: Gaussian Filter (kernel 5x5)")
        self.status_var.set("Gaussian Filter selesai.")

    # ===================== 4. DETEKSI TEPI =====================
    def proses_sobel(self):
        if not self._cek_gambar(): return
        gray = cv2.cvtColor(self.gambar_asli, cv2.COLOR_BGR2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        self.gambar_proses = cv2.convertScaleAbs(np.sqrt(sobelx**2 + sobely**2))
        self.tampilkan_gambar(self.gambar_proses)
        self.nama_proses.set("Proses: Sobel Edge Detection")
        self.status_var.set("Sobel Edge Detection selesai.")

    def proses_canny(self):
        if not self._cek_gambar(): return
        gray = cv2.cvtColor(self.gambar_asli, cv2.COLOR_BGR2GRAY)
        self.gambar_proses = cv2.Canny(gray, 100, 200)
        self.tampilkan_gambar(self.gambar_proses)
        self.nama_proses.set("Proses: Canny Edge Detection (threshold 100-200)")
        self.status_var.set("Canny Edge Detection selesai.")

    # ===================== 5. SEGMENTASI CITRA =====================
    def proses_threshold(self):
        if not self._cek_gambar(): return
        gray = cv2.cvtColor(self.gambar_asli, cv2.COLOR_BGR2GRAY)
        _, self.gambar_proses = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        self.tampilkan_gambar(self.gambar_proses)
        self.nama_proses.set("Proses: Threshold Segmentation (nilai=127)")
        self.status_var.set("Threshold Segmentation selesai.")

    def proses_kmeans(self):
        if not self._cek_gambar(): return
        K = 3
        img = self.gambar_asli.copy()
        Z = img.reshape((-1, 3)).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, label, center = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        center = np.uint8(center)
        res = center[label.flatten()]
        self.gambar_proses = res.reshape(img.shape)
        self.tampilkan_gambar(self.gambar_proses)
        self.nama_proses.set(f"Proses: K-Means Segmentation (K={K})")
        self.status_var.set(f"K-Means Segmentation (K={K}) selesai.")


if __name__ == "__main__":
    root = tk.Tk()
    app = AplikasiPengolahanCitra(root)
    root.mainloop()