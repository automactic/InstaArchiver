import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { environment } from 'src/environments/environment';
import { APIService } from '../api.service';
import { Profile } from '../entities';


@Component({
  selector: 'app-profile-detail',
  templateUrl: './profile-detail.component.html',
  styleUrls: ['./profile-detail.component.scss']
})
export class ProfileDetailComponent implements OnInit {
  profile$: Observable<Profile>;
  username?: string;

  constructor(private route: ActivatedRoute, private router: Router, private apiService: APIService) {
    this.profile$ = this.route.paramMap.pipe(
      switchMap(params => {
        return this.apiService.getProfile(params.get("username") ?? "")
      })
    );
  }

  ngOnInit(): void {
    console.log('test')
  }

  profileImagePath(filename: string): string {
    return `${environment.apiRoot}/media/profile_images/${filename}`
  }
}
